import json
import socket
import threading
from time import sleep
from datetime import date, datetime, timedelta, time
import arrow

import dateutil.parser
import pytz
from pytz import timezone
from apscheduler.scheduler import Scheduler
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import sessionmaker

from rootio.config import DefaultConfig
from rootio.content import ContentMusicArtist, ContentMusicAlbum, ContentMusic, ContentMusicPlaylist, \
    ContentMusicPlaylistItem
from rootio.radio.models import ScheduledProgram
from sqlalchemy import text, create_engine

from radio_program import RadioProgram
from db_agent import DBAgent

class ProgramHandler:

    def __init__(self, radio_station):
        self.__radio_station = radio_station
        self.__scheduler = None
        self.__scheduled_jobs = None
        self.__start_listeners()
        self.__is_starting_up = True
        self.__running_program = None
        self.__in_sync = False
        self.__time_stamp = None
        self.__interval_hours = 3  # Time after which to schedule again
        self.__radio_station.logger.info("Done initialising ProgramHandler for {0}".format(radio_station.station.name))

    def run(self):
        self.run_current_schedule()
        self.__is_starting_up = False

    def __prepare_schedule(self):
        self.__load_programs()
        self.__scheduler = Scheduler(timezone=pytz.utc)
        self.__scheduled_jobs = dict()

    def run_current_schedule(self):
        self.__prepare_schedule()
        self.__scheduler.start()
        self.__schedule_programs()
        #self.__schedule_next_schedule()

    def set_running_program(self, running_program):
        self.__stop_program()
        self.__running_program = running_program

    def stop(self):
        self.__stop_program()
        # any clean up goes here
        # unschedule stuff

    def __schedule_next_schedule(self):
        base_date = datetime.now()
        next_schedule_date = base_date + timedelta(0, 0, 0, 0, 0, self.__interval_hours)  # 3 hours
        self.__scheduler.add_date_job(getattr(self, 'run_current_schedule'), next_schedule_date)

    def __schedule_programs(self):
        for scheduled_program in self.__scheduled_programs:
            if not self.__is_program_expired(scheduled_program):
                self.__add_scheduled_job(scheduled_program)
                self.__radio_station.logger.info(
                    "Scheduled program {0} for station {1} starting at {2}".format(scheduled_program.program.name,
                                                                                   self.__radio_station.station.name,
                                                                                   scheduled_program.start))

    def __add_scheduled_job(self, scheduled_program):
        start_time = self.__get_program_start_time(scheduled_program).replace(tzinfo=None)
        program = RadioProgram(scheduled_program, self.__radio_station, self)
        try:
            scheduled_job = self.__scheduler.add_date_job(getattr(program, 'start'),  start_time)
            self.__scheduled_jobs[scheduled_program.id] = scheduled_job
        except Exception as e:
            self.__radio_station.logger.error("Error {err} in __add_scheduled_job".format(err=e.message))

    def __delete_scheduled_job(self, index):
        if not self.__scheduled_jobs:
            self.__radio_station.logger.warning("Failed to delete job (no jobs are scheduled)")
            return

        if index in self.__scheduled_jobs:
            try:
                self.__scheduler.unschedule_job(self.__scheduled_jobs[index])
            except:
                # The job probably ran already
                self.__radio_station.logger.warning("Failed to remove unscheduled job #{}".format(index))
            del self.__scheduled_jobs[index]

        # Stop the program if it is running
        if self.__running_program is not None and self.__running_program.id == index:
            self.__running_program.stop()

    def __stop_program(self):
        try:
            if self.__running_program is not None:
                self.__running_program.stop()
                sleep(2)
        except:
            return

    def __run_program(self):
        # self.__running_program.run()
        return

    def __load_programs(self):
        timezone = self.__radio_station.station.timezone
        #if self.__is_starting_up:
        date_filter = "((date(start) = date(now())) or (start < now() and radio_scheduledprogram.end > now()))"
        #else:
        #   date_filter = "(start >= now() at time zone '{tz}' and start < now() at time zone '{tz}' + interval '{interval} hour')".format(
        #        tz=timezone, interval=self.__interval_hours)
        query = self.__radio_station.db.query(ScheduledProgram).filter(
            ScheduledProgram.station_id == self.__radio_station.station.id).filter(text(date_filter)).filter(
            ScheduledProgram.deleted == False)
        self.__scheduled_programs = query.all()
        self.__radio_station.logger.info("Loaded {1} programs for {0}".format(self.__radio_station.station.name, len(self.__scheduled_programs)))

    def __load_program(self, program_id):
        self.__radio_station.db._model_changes = {}
        self.__radio_station.db.commit()
        return self.__radio_station.db.query(ScheduledProgram).filter(ScheduledProgram.id == program_id).first()

    def __start_listeners(self):
        t = threading.Thread(target=self.__listen_for_scheduling_changes,
                             args=(DefaultConfig.SCHEDULE_EVENTS_SERVER_IP, DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))
        t.start()

    def __listen_for_scheduling_changes(self, ip, port):
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (ip, port)

        # It may not be possible to connect after restart, TIME_WAIT could come into play etc. Anyway, keep trying
        connected = False
        while not connected:
            try:
                sck.connect(addr)
                connected = True
            except:
                self.__radio_station.logger.warning(
                    "[Station #{}] Could not connect to server, retrying in 30..."
                    .format(self.__radio_station.id))
                sleep(30)
        sck.sendall(json.dumps({'station': self.__radio_station.station.id, 'action': 'register'}))

        while True:
            data = sck.recv(10240000)

            try:
                event = json.loads(data)
            except:
                incomplete_data = True
                total_data=[]
                total_data.append(data)

                while incomplete_data:
                    #self.__radio_station.logger.debug('getting chunks...')
                    try:
                        partial_data = sck.recv(10240000)
                    except Exception as e:
                        self.__radio_station.logger.error('Failed to get all data chunks... {}'.format(e.message))
                    if partial_data:
                        total_data.append(partial_data)

                    try:
                        json.loads(''.join(total_data))
                        incomplete_data = False
                    except:
                        pass

                data = ''.join(total_data)
                try:
                    event = json.loads(data)
                except Exception as e:
                    self.__radio_station.logger.error("Error 1 {err} in ProgramHandler.__listen_for_scheduling_changes".format(err=e.message))
                    return

            try:
                if "action" in event and "id" in event:
                    if event["action"] == "delete":
                        self.__delete_scheduled_job(event["id"])
                        self.__radio_station.logger.info(
                            "Scheduled program with id {0} has been deleted"
                                .format(event["id"]))
                    elif event["action"] == "add":
                        scheduled_program = self.__load_program(event["id"])
                        self.__radio_station.logger.info(
                                "Will Schedule program with id {0}"
                                    .format(event["id"]))
                        if not self.__is_program_expired(scheduled_program):
                            self.__add_scheduled_job(scheduled_program)
                            self.__radio_station.logger.info(
                                "Scheduled program with id {0} has been added at time {1}"
                                    .format(event["id"], scheduled_program.start))
                    elif event["action"] == "update":
                        self.__delete_scheduled_job(event["id"])
                        scheduled_program = self.__load_program(event["id"])
                        self.__radio_station.db.refresh(scheduled_program)
                        if not self.__is_program_expired(scheduled_program):
                            self.__add_scheduled_job(scheduled_program)
                            self.__radio_station.logger.info(
                                "Scheduled program with id {0} has been moved to start at time {1}"
                                    .format(event["id"], scheduled_program.start))
                    elif event["action"] == "sync":
                        if not self.__in_sync:
                            self.__in_sync = True
                            self.__timestamp = datetime.now().isoformat()
                            #  self.__radio_station.logger.info("Syncing music for station {0}".format(event["id"]))
                            t = threading.Thread(target=self.__process_music_data, args=(event["id"], event["music_data"], self.__timestamp))
                            t.start()
                            #send a response
                        sck.sendall(json.dumps({'status': True, 'date': self.__timestamp}))
 
            except Exception as e:
                self.__radio_station.logger.error("Error 2 {err} in ProgramHandler.__listen_for_scheduling_changes".format(err=e.message))

    def __get_dict_from_rows(self, rows):
        result = dict()
        for row in rows:
            result[row.title] = row
        return result

    def __process_music_data(self, station_id, json_string, timestamp):
        sync_date = dateutil.parser.parse(timestamp)
        self.__radio_station.logger.info("Starting music sync for {dt}".format(dt=sync_date.isoformat()))
        session = DBAgent.get_session() 
        songs_in_db = self.__get_dict_from_rows(session.query(ContentMusic).filter(ContentMusic.station_id == station_id).all())
        artists_in_db = self.__get_dict_from_rows(
            session.query(ContentMusicArtist).filter(ContentMusicArtist.station_id == station_id).all())
        albums_in_db = self.__get_dict_from_rows(
            session.query(ContentMusicAlbum).filter(ContentMusicAlbum.station_id == station_id).all())
        session.close()

        #session = DBAgent.get_session()
        data = json.loads(json_string)
        for artist in data:
            if artist in artists_in_db:
                music_artist = artists_in_db[artist]
                session.query(ContentMusicArtist).filter(ContentMusicArtist.id == music_artist.id).update({'updated_at': sync_date})
                #music_artist.updated_at = sync_date
            else:
                # persist the artist
                music_artist = ContentMusicArtist(**{'title': artist, 'station_id': station_id})
                music_artist.updated_at = sync_date
                artists_in_db[artist] = music_artist
                session.add(music_artist)
            try:
                session._model_changes = {}
                session.commit()
            except DatabaseError:
                session.rollback()
                continue
            except:
                    continue

            for album in data[artist]:
                if album in albums_in_db:
                    music_album = albums_in_db[album]
                    session.query(ContentMusicAlbum).filter(ContentMusicAlbum.id == music_album.id).update({'updated_at': sync_date})
                    #music_album.updated_at = sync_date
                else:
                    # persist the album
                    music_album = ContentMusicAlbum(**{'title': album, 'station_id': station_id})
                    music_album.updated_at = sync_date
                    albums_in_db[album] = music_album
                    session.add(music_album)
                try:
                    session._model_changes = {}
                    session.commit()
                except DatabaseError:
                    session.rollback()
                    continue
                except:
                    continue

                for song in data[artist][album]['songs']:
                    if song['title'] in songs_in_db:
                        music_song = songs_in_db[song['title']]
                        session.query(ContentMusic).filter(ContentMusic.id == music_song.id).update({'updated_at': sync_date})
                        #music_song.updated_at = sync_date
                    else:
                        music_song = ContentMusic(
                            **{'title': song['title'], 'duration': song['duration'], 'station_id': station_id,
                               'album_id': music_album.id, 'artist_id': music_artist.id})
                        music_song.updated_at = sync_date
                        songs_in_db[song['title']] = music_song
                        session.add(music_song)
                    try:
                        session._model_changes = {}
                        session.commit()
                    except DatabaseError:
                        session.rollback()
                        continue
                    except:
                        continue

        try:
            session.close()
        except Exception as e:
            self.__radio_station.logger.error(
                "Error 2 {err} in ProgramHandler.__process_music_data".format(err=e.message))

        self.__delete_absent_records(sync_date, station_id)

        self.__in_sync = False
        self.__radio_station.logger.info("Done with music sync for {dt}".format(dt=sync_date.isoformat()))

    def __delete_absent_records(self, sync_date, station_id):
        self.__radio_station.logger.info("Removing audio content older than {dt}".format(dt=sync_date.isoformat()))
        session = DBAgent.get_session()
        songs = session.query(ContentMusic).filter(ContentMusic.updated_at < sync_date, ContentMusic.station_id == station_id).all()
        for song in songs:
            self.__radio_station.logger.info("Removing non-existent song {sng}".format(sng=song.title))
            session.query(ContentMusicPlaylistItem).filter(ContentMusicPlaylistItem.playlist_item_type_id == 1,
                                                           ContentMusicPlaylistItem.playlist_item_id == song.id).delete()
            session.delete(song)
            session._model_changes = {}
            session.commit()
        session.close()
        
        session = DBAgent.get_session()
        albums = session.query(ContentMusicAlbum).filter(ContentMusicAlbum.updated_at < sync_date, ContentMusicAlbum.station_id == station_id).all()
        for album in albums:
            self.__radio_station.logger.info("Removing non-existent album {alb}".format(alb=album.title))
            session.query(ContentMusicPlaylistItem).filter(
                    ContentMusicPlaylistItem.playlist_item_type_id == 2, ContentMusicPlaylistItem.playlist_item_id == album.id).delete()
            session.delete(album)
            session._model_changes = {}
            session.commit()
        session.close()

        session = DBAgent.get_session()
        artists = session.query(ContentMusicArtist).filter(ContentMusicArtist.updated_at < sync_date, ContentMusicArtist.station_id == station_id).all()
        for artist in artists:
            self.__radio_station.logger.info("Removing non-existent artist {art}".format(art=artist.title))
            session.query(ContentMusicPlaylistItem).filter(
                    ContentMusicPlaylistItem.playlist_item_type_id == 3, ContentMusicPlaylistItem.playlist_item_id == artist.id).delete()
            session.delete(artist)
            session._model_changes = {}
            session.commit()
        session.close()

    """
    Gets the program to run from the current list of programs that are lined up for the day
    """
    def __get_current_program(self):
        for program in self.__scheduled_programs:
            if not self.__is_program_expired(program):
                return program

    """
    Returns whether or not the time for a particular program has passed
    """
    def __is_program_expired(self, scheduled_program):
        now = arrow.utcnow()
        return (scheduled_program.start + scheduled_program.program.duration) < (now + timedelta(minutes=1))

    def __get_program_start_time(self, scheduled_program):
        now = arrow.utcnow().datetime
        if scheduled_program.start < now:  # Time at which program begins is already past
            return now + timedelta(seconds=5)  # 5 second scheduling allowance
        else:
            return scheduled_program.start + timedelta(seconds=5)  # 5 second scheduling allowance
