# -*- coding: utf-8 -*-
import json

from flask import Blueprint, current_app, request, jsonify, abort, make_response, json
from flask.ext.login import login_user, current_user, logout_user
from sqlalchemy.exc import DatabaseError

from .utils import parse_datetime
#from ..app import music_file_uploads
from ..content import ContentMusic, ContentMusicAlbum, ContentMusicArtist, ContentMusicPlaylist, \
    ContentMusicPlaylistItem, ContentPodcast, ContentPodcastDownload
from ..decorators import returns_json, restless_preprocessors, restless_postprocessors, api_key_or_auth_required
from ..extensions import db, rest, csrf
from ..radio.models import Network, Station, Person, Program, ScheduledProgram, Episode, Recording, StationAnalytic
from ..telephony import PhoneNumber, Call, Message
from ..user import User
from ..utils import jquery_dt_paginator

# the web login api
api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated():
        return jsonify(flag='success')

    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        user, authenticated = User.authenticate(username, password)
        if user and authenticated:
            if login_user(user, remember='y'):
                return jsonify(flag='success')

    current_app.logger.debug('login failed, username: %s.' % username)
    return jsonify(flag='fail', msg='Sorry, try again.')


@api.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return jsonify(flag='success', msg='Logged out.')


# the restless api
# needs to be called after app instantiation
# preprocessor requires logged in user or api key
def restless_routes():
    rest.create_api(Person, collection_name='person', methods=['GET'],
                    preprocessors=restless_preprocessors,
                    postprocessors=restless_postprocessors)
    rest.create_api(User, collection_name='user', methods=['GET'],
                    exclude_columns=['_password'],
                    preprocessors=restless_preprocessors)

    # rest.create_api(Station, collection_name='station', methods=['GET'],
    #  exclude_columns=['owner','api_key','scheduled_programs','analytics','blocks']) #,
    # preprocessors=restless_preprocessors,
    # postprocessors=restless_postprocessors)
    rest.create_api(Program, collection_name='program', methods=['GET'],
                    exclude_columns=['scheduled_programs', ],
                    preprocessors=restless_preprocessors)
    rest.create_api(ScheduledProgram, collection_name='scheduledprogram', methods=['GET'],
                    exclude_columns=['station'],
                    preprocessors=restless_preprocessors)

    rest.create_api(Episode, collection_name='episode', methods=['GET'],
                    exclude_columns=[],
                    preprocessors=restless_preprocessors)
    rest.create_api(Recording, collection_name='recording', methods=['GET'],
                    exclude_columns=[],
                    preprocessors=restless_preprocessors)

    rest.create_api(PhoneNumber, collection_name='phonenumber', methods=['GET'],
                    exclude_columns=[],
                    preprocessors=restless_preprocessors)
    rest.create_api(Call, collection_name='call', methods=['GET'],
                    exclude_columns=[],
                    preprocessors=restless_preprocessors)
    rest.create_api(Message, collection_name='message', methods=['GET'],
                    exclude_columns=[],
                    preprocessors=restless_preprocessors)


# need routes for:
# phone to update station schedule?

# non CRUD-routes
# protect with decorator

@api.route('/station', methods=['GET'])
@returns_json
def stations():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    responses = []
    for station in stations:
        response = dict()
        if station is not None:
            response["name"] = station.name
            response["frequency"] = station.frequency
            response["network_id"] = station.network_id
            if station.location is not None:
                response["location"] = {"name": station.location.name, "latitude": station.location.latitude,
                                        "longitude": station.location.longitude}
            if station.primary_transmitter_phone is not None:
                response["primary_transmitter_telephone"] = station.primary_transmitter_phone.raw_number
            if station.secondary_transmitter_phone is not None:
                response["secondary_transmitter_telephone"] = station.secondary_transmitter_phone.raw_number
            response["multicast_IP"] = station.broadcast_ip
            response["multicast_port"] = station.broadcast_port

        responses.append(response)
    all_responses = dict()
    all_responses["objects"] = responses
    return all_responses


@api.route('/station/<int:station_id>/information', methods=['GET', 'POST'])
@api_key_or_auth_required
@csrf.exempt
@returns_json
def station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    response = dict()
    if station is not None:
        response["name"] = station.name
        response["frequency"] = station.frequency
        if station.location is not None:
            response["location"] = {"name": station.location.name, "latitude": station.location.latitude,
                                    "longitude": station.location.longitude}
        if station.primary_transmitter_phone is not None:
            response["primary_transmitter_telephone"] = station.primary_transmitter_phone.raw_number
        if station.secondary_transmitter_phone is not None:
            response["secondary_transmitter_telephone"] = station.secondary_transmitter_phone.raw_number
        response["multicast_IP"] = station.broadcast_ip
        response["multicast_port"] = station.broadcast_port
        response["sip_settings"] = {"sip_username": station.sip_username, "sip_password": station.sip_password,
                                    "sip_domain": station.sip_server, "sip_port": station.sip_port,
                                    "sip_protocol": station.sip_protocol,
                                    "sip_reregister_period": station.sip_reregister_period,
                                    "sip_stun": station.sip_stun_server, "call_volume": station.call_volume}
        response["tts_accent"] = station.tts_accent
        response["tts_gender"] = station.tts_gender
        if station.tts_language is not None:
            response["tts_language"] = station.tts_language.name
        response["tts_audio_format"] = station.tts_audio_format
        response["tts_sample_rate"] = station.tts_sample_rate
        response["media_volume"] = station.audio_volume
    responses = dict()
    responses["station"] = response
    return responses


@api.route('/station/<int:station_id>/current_program', methods=['GET'])
# @api_key_or_auth_required
@returns_json
def current_program(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.current_program()


@api.route('/station/<int:station_id>/on_air', methods=['GET'])
# @api_key_or_auth_required
@returns_json
def on_air(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    current_program = station.current_program()
    if current_program:
        return current_program.onairprogram
    else:
        message = jsonify(flag='error', msg='No OnAirProgram set for station')
        abort(make_response(message, 500))


@api.route('/station/<int:station_id>/next_program', methods=['GET'])
# @api_key_or_auth_required
@returns_json
def next_program(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.next_program()


@api.route('/station/<int:station_id>/current_block', methods=['GET'])
# @api_key_or_auth_required
@returns_json
def current_block(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.current_block()


@csrf.exempt
@api.route('/station/<int:station_id>/schedule', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def station_schedule(station_id):
    """API method to get a station's schedule.
        start: ISO datetime
        end: ISO datetime
        all: if truthy, then ignores start and end constraints"""
    try:
        start = parse_datetime(request.args.get('start'))
        end = parse_datetime(request.args.get('end'))
    except (ValueError, TypeError):
        message = jsonify(flag='error', msg="Unable to parse updated_since parameter. Must be ISO datetime format")
        abort(make_response(message, 400))
    # TODO, investigate the proper ordering of these clauses for query speed
    if request.args.get('all'):
        scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
            ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).all()
    elif start and end:
        scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
            ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).filter(
            ScheduledProgram.start > start).filter(ScheduledProgram.end > end).all()
    elif start:
        scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
            ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).filter(
            ScheduledProgram.start > start).all()
    elif end:
        scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
            ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).filter(
            ScheduledProgram.end > end).all()
    else:
        message = jsonify(flag='error', msg="Need to specify parameters 'start' or 'end' as ISO datetime or all=1")
        abort(make_response(message, 400))
    responses = []
    for program in scheduled_programs:
        response = dict()
        response['name'] = program.Program.name
        response['scheduled_program_id'] = program.ScheduledProgram.id
        response['start'] = program.ScheduledProgram.start
        response['end'] = program.ScheduledProgram.end
        response['updated_at'] = program.ScheduledProgram.updated_at
        response['deleted'] = program.ScheduledProgram.deleted
        response['structure'] = program.Program.structure
        responses.append(response)
    all_responses = {"scheduled_programs": responses}
    return all_responses


@api.route('/station/<int:station_id>/programs', methods=['GET', 'POST'])
# @api_key_or_auth_required
@csrf.exempt
@returns_json
def station_programs(station_id):
    """API method to get all programs currently scheduled on the station"""

    if request.args.get('updated_since'):
        try:
            updated_since = parse_datetime(request.args.get('updated_since'))
            scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
                ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).filter(
                ScheduledProgram.updated_at > updated_since).all()
        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400))
    else:
        scheduled_programs = db.session.query(Program, ScheduledProgram).filter(
            ScheduledProgram.station_id == station_id).filter(ScheduledProgram.program_id == Program.id).all()
    responses = []
    for program in scheduled_programs:
        response = dict()
        response['name'] = program.Program.name
        response['scheduled_program_id'] = program.ScheduledProgram.id
        response['program_type_id'] = program.Program.program_type_id
        response['start'] = program.ScheduledProgram.start
        response['end'] = program.ScheduledProgram.end
        response['updated_at'] = program.ScheduledProgram.updated_at
        response['deleted'] = program.ScheduledProgram.deleted
        response['structure'] = program.Program.structure
        responses.append(response)
    all_responses = {"scheduled_programs": responses}
    return all_responses


@csrf.exempt
@api.route('/station/<int:station_id>/analytics', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def station_analytics(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()
    data = json.loads(request.data)
    responses = []

    for single_analytic_data in data['analytic_data']:
        response = dict()
        response['id'] = single_analytic_data['id']
        del (single_analytic_data['id'])
        analytic = StationAnalytic(**single_analytic_data)  # use this format to avoid multidict-type issue
        analytic.station = station
        db.session.add(analytic)
        try:
            db.session.commit()
            response['status'] = True
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            response['status'] = False
            response['error'] = e.message
        responses.append(response)
    all_responses = {"results": responses}
    return all_responses


@csrf.exempt
@api.route('/station/<int:station_id>/whitelist', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def station_whitelist(station_id):
    """API method to get whitelist for a station"""
    # whitelist is a concatenation of outgoing gateways and
    station = Station.query.filter_by(id=station_id).first_or_404()
    whitelists = station.whitelist_number
    whitelist_numbers = []
    for number in whitelists:
        whitelist_number = number.number
        whitelist_numbers.append(whitelist_number)
    # add the gateways
    for gw in station.outgoing_gateways:
        whitelist_numbers.append(str(gw.number_bottom))
    all_responses = {"whitelist": whitelist_numbers}
    return all_responses


@csrf.exempt
@api.route('/station/<int:station_id>/frequency_update', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def frequency_update(station_id):
    """API method to get the frequency of updates for a station"""
    station = Station.query.filter_by(id=station_id).first_or_404()

    diagnostic = {"interval": station.analytic_update_frequency, "unit": "seconds"}
    synchronization = {"interval": station.client_update_frequency, "unit": "seconds"}
    response = {"synchronization": synchronization, "diagnostics": diagnostic}
    return response


@csrf.exempt
@api.route('/station/<int:station_id>/call', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def call_data(station_id):
    """API method to get or post analytics for a station"""

    data = json.loads(request.data)
    responses = []

    for single_call_data in data['call_data']:
        response = dict()
        response['id'] = single_call_data['call_uuid']
        call_details = Call(**single_call_data)  # use this format to avoid multidict-type issue
        call_details.station_id = station_id
        db.session.add(call_details)
        try:
            db.session.commit()
            response['status'] = True
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            response['status'] = False
            response['error'] = e.message
        responses.append(response)
    all_responses = {"results": responses}
    return all_responses


@csrf.exempt
@api.route('/station/<int:station_id>/message', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def message_data(station_id):
    """API method to get or post analytics for a station"""

    data = json.loads(request.data)
    responses = []

    for single_message_data in data['message_data']:
        response = dict()
        response['id'] = single_message_data['message_uuid']
        message_details = Message(**single_message_data)  # use this format to avoid multidict-type issue
        message_details.station_id = station_id
        db.session.add(message_details)
        try:
            db.session.commit()
            response['status'] = True
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            response['status'] = False
            response['error'] = e.message
        responses.append(response)
    all_responses = {"results": responses}
    return all_responses


@api.route('/program/<int:program_id>/episodes', methods=['GET', 'POST'])
# @api_key_or_auth_required
@returns_json
def program_episodes(program_id):
    """API method to get all episodes currently available for a program"""
    program = Program.query.filter_by(id=program_id).first_or_404()
    episodes = program.episodes

    if request.args.get('updated_since'):
        try:
            updated_since = parse_datetime(request.args.get('updated_since'))
            return episodes.filter(Episode.updated_at > updated_since)
        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400))
    else:
        return episodes.all()


@api.route('/podcast/<int:podcast_id>/downloads', methods=['GET', 'POST'])
# @api_key_or_auth_required
# @returns_json
@csrf.exempt
def podcast_downloads(podcast_id):
    """API method to get all episodes currently available for a program"""

    cols = [ContentPodcastDownload.date_published, ContentPodcastDownload.summary, ContentPodcastDownload.file_name]
    downloads = ContentPodcastDownload.query.with_entities(*cols).join(ContentPodcast).filter(
        ContentPodcast.id == podcast_id)

    records = jquery_dt_paginator.get_records(downloads,
                                              [ContentPodcastDownload.file_name, ContentPodcastDownload.summary],
                                              request)
    return jsonify(records)


def get_dict_from_rows(rows):
    result = dict()
    for row in rows:
        result[row.title] = row
    return result


@api.route('/station/<int:station_id>/music', methods=['GET', 'POST'])
# @api_key_or_auth_required
@csrf.exempt
@returns_json
def music_sync(station_id):
    """API method to grab music from the phone and  store it online"""
    from rootio.app import music_file_uploads
    music_file_uploads.append((station_id, request.data))
    #t = threading.Thread(target=process_music_data, args=(station_id, request.data))
    #t.start()
    #process_music_data(station_id, request.data)

    return {'status': True}  # TODO: Make the status dependent on the result of the upload


def process_music_data(station_id, json_string):
    songs_in_db = get_dict_from_rows(ContentMusic.query.filter(ContentMusic.station_id == station_id).all())
    artists_in_db = get_dict_from_rows(
        ContentMusicArtist.query.filter(ContentMusicArtist.station_id == station_id).all())
    albums_in_db = get_dict_from_rows(ContentMusicAlbum.query.filter(ContentMusicAlbum.station_id == station_id).all())

    data = json.loads(json_string)
    for artist in data:
        if artist in artists_in_db:
            music_artist = artists_in_db[artist]
        else:
            # persist the artist
            music_artist = ContentMusicArtist(**{'title': artist, 'station_id': station_id})
            artists_in_db[artist] = music_artist
            db.session.add(music_artist)
            try:
                db.session.commit()
            except DatabaseError:
                db.session.rollback()
                continue

        for album in data[artist]:
            if album in albums_in_db:
                music_album = albums_in_db[album]
            else:
                # persist the album
                music_album = ContentMusicAlbum(**{'title': album, 'station_id': station_id})
                albums_in_db[album] = music_album
                db.session.add(music_album)
                try:
                    db.session.commit()
                except DatabaseError:
                    db.session.rollback()
                    continue

            for song in data[artist][album]['songs']:
                if song['title'] in songs_in_db:
                    music_song = songs_in_db[song['title']]
                else:
                    music_song = ContentMusic(
                        **{'title': song['title'], 'duration': song['duration'], 'station_id': station_id,
                           'album_id': music_album.id, 'artist_id': music_artist.id})
                    songs_in_db[song['title']] = music_song
                db.session.add(music_song)
                try:
                    db.session.commit()
                except DatabaseError:
                    db.session.rollback()
                    continue


@api.route('/station/<int:station_id>/playlists', methods=['GET', 'POST'])
# @api_key_or_auth_required
@csrf.exempt
@returns_json
def music_playlist(station_id):
    playlists = ContentMusicPlaylist.query.filter(ContentMusicPlaylist.station_id == station_id).all()
    play_list = []

    for playlist in playlists:
        pl = dict()
        pl['title'] = playlist.title
        # get the songs
        songs = ContentMusic.query.join(ContentMusicPlaylistItem,
                                        ContentMusicPlaylistItem.playlist_item_id == ContentMusic.id).with_entities(
            ContentMusic.title).filter(ContentMusicPlaylistItem.playlist_item_type_id == 1).filter(
            ContentMusicPlaylistItem.deleted == False).filter(
            ContentMusicPlaylistItem.playlist_id == playlist.id).filter(ContentMusic.station_id == station_id).all()
        pl['songs'] = songs

        # get the artists
        artists = ContentMusicArtist.query.join(ContentMusicPlaylistItem,
                                                ContentMusicPlaylistItem.playlist_item_id == ContentMusicArtist.id).with_entities(
            ContentMusicArtist.title).filter(ContentMusicPlaylistItem.playlist_item_type_id == 3).filter(
            ContentMusicPlaylistItem.deleted == False).filter(
            ContentMusicPlaylistItem.playlist_id == playlist.id).filter(
            ContentMusicArtist.station_id == station_id).all()
        pl['artists'] = artists

        # get the albums
        albums = ContentMusicAlbum.query.join(ContentMusicPlaylistItem,
                                              ContentMusicPlaylistItem.playlist_item_id == ContentMusicAlbum.id).with_entities(
            ContentMusicAlbum.title).filter(ContentMusicPlaylistItem.playlist_item_type_id == 2).filter(
            ContentMusicPlaylistItem.deleted == False).filter(
            ContentMusicPlaylistItem.playlist_id == playlist.id).filter(
            ContentMusicAlbum.station_id == station_id).all()
        pl['albums'] = albums

        play_list.append(pl)

    return play_list
