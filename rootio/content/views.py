# -*- coding: utf-8 -*-welcome_message_file = FileField('Welcome message')

import os
import pytz
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, jsonify, url_for
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user
from werkzeug.utils import secure_filename

from .forms import ContentMusicPlaylistForm, ContentTrackForm, ContentUploadForm, ContentPodcastForm, ContentStreamForm, CommunityMenuForm
from .models import ContentMusicPlaylistItem, ContentMusicPlaylist, ContentTrack, ContentUploads, ContentStream, \
    ContentPodcast, CommunityMenu, CommunityContent
from ..config import DefaultConfig
from ..extensions import db, csrf
from ..radio.forms import PersonForm
from ..radio.models import ContentType, Person, Network, Station
from ..user.models import User
from ..utils import jquery_dt_paginator, upload_to_s3, make_dir, save_uploaded_file

ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

content = Blueprint('content', __name__, url_prefix='/content')


@content.route('/')
@login_required
def index():
    # re-write using ORM
    # Filter by network when Track contains network id, filter by uploader
    status_query = "select ct.id, ct.name \"track\", rct.name \"content type\", count(*) \"uploads\" , " \
                   "(select count(*) from radio_program where structure like '%'||ct.description||'%') " \
                   "\"subscriptions\" from content_track as ct join content_type as rct on \"ct\".type_id = rct.id " \
                   "join content_uploads as cu on ct.id = cu.track_id  group by ct.id, rct.name"
    contents = db.session.execute(status_query)
    return render_template('content/index.html', content=contents)


@content.route('/upload', methods=['POST'])
@login_required
def upload():
    form = ContentMusicForm(request.form)
    return render_template('content/track_files_add.html', form=form)


@content.route('/tracks/')
@login_required
def list_tracks():
    networks = current_user.networks
    network_ids = [network.id for network in networks]
    show_only = request.args.get('show_only', '')

    if show_only:
        tracks = db.session.query(ContentTrack).join(ContentTrack.networks).filter_by(id = show_only)
    else:
        tracks = db.session.query(ContentTrack).join(ContentTrack.networks).filter(Network.id.in_(network_ids))

    return render_template('content/tracks.html', tracks=tracks, networks=networks, active='tracks', show_only=show_only)


@content.route('/tracks/<int:track_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def track_delete(track_id):
    track = ContentTrack.query.filter_by(id=track_id).first_or_404()

    track.deleted = True

    try:
        db.session.add(track)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/tracks/<int:track_id>/files', methods=['GET'])
@login_required
def list_track_files(track_id):
    track = ContentTrack.query.filter_by(id=track_id).first_or_404()
    return render_template('content/track_files.html', track=track, active='tracks')


@content.route('/tracks/<int:track_id>/files/empty', methods=['GET'])
@login_required
def track_files_empty(track_id):
    track = ContentTrack.query.filter_by(id=track_id).first_or_404()

    paths = []

    for uploaded_file in track.files:
        paths.append(
            '{}/{}'.format(DefaultConfig.CONTENT_DIR, uploaded_file.uri)
        )
        db.session.delete(uploaded_file)


    try:
        db.session.commit()
        for file_path in paths:
            os.remove(file_path)
    except:
        pass
        # import ipdb; ipdb.set_trace()

    return redirect(url_for('content.list_track_files', track_id=track.id))


@content.route('/tracks/<int:track_id>/files/add', methods=['GET'])
@login_required
def track_files_add(track_id):
    track = ContentTrack.query.filter_by(id=track_id).first_or_404()
    form = ContentUploadForm()
    return render_template('content/track_files_add.html', track=track, form=form)


@content.route('/tracks/<int:track_id>', methods=['GET', 'POST'])
@login_required
def track(track_id):
    tracks = ContentTrack.query.filter_by(id=track_id).first_or_404()
    form = ContentTrackForm(obj=tracks, next=request.args.get('next'))


    if form.validate_on_submit():
        form.populate_obj(tracks)

        db.session.add(tracks)
        db.session.commit()
        flash(_('Track updated.'), 'success')
    return render_template('content/track.html', tracks=tracks, form=form)


@content.route('/tracks/add/', methods=['GET', 'POST'])
@login_required
def track_add():
    form = ContentTrackForm(request.form)
    tracks = None
    if form.validate_on_submit():

        cleaned_data = form.data  # make a copy
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data.pop('submit', None)  # remove submit field from list
        tracks = ContentTrack(**cleaned_data)  # create new object from data
        db.session.add(tracks)
        db.session.commit()
        flash(_('Track added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
    return render_template('content/track.html', tracks=tracks, form=form)


@content.route('/uploads/')
@login_required
def list_content_uploads():
    content_uploads = ContentUploads.query.filter_by(uploaded_by=current_user.id).all()
    return render_template('content/content_uploads.html', content_uploads=content_uploads)


@content.route('/uploads/<int:content_upload_id>', methods=['GET', 'POST'])
@login_required
def content_upload(content_upload_id):
    content_uploads = ContentUploads.query.filter_by(id=content_upload_id).first_or_404()
    form = ContentUploadForm(obj=content_uploads, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_uploads)

        db.session.add(content_uploads)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_upload.html', content_uploads=content_uploads, form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@content.route('/uploads/add/', methods=['GET', 'POST'])
@login_required
def content_upload_add():
    form = ContentUploadForm(request.form)
    content_uploads = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash(_('No file part'))
            return redirect(request.url)
        uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploaded_file.filename == '':
            flash(_('No selected file'))
            return redirect(request.url)
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)

        if form.validate_on_submit():
            cleaned_data = form.data  # make a copy
            cleaned_data['uploaded_by'] = current_user.id
            cleaned_data['name'] = filename
            cleaned_data['type_id'] = cleaned_data['contenttrack_id'].type_id
            cleaned_data['track_id'] = cleaned_data['contenttrack_id'].id

            uploaded_file_name = str(cleaned_data['contenttrack_id'])
            upload_directory = str(current_user.id)
            uri = save_uploaded_file(uploaded_file, upload_directory, file_name=uploaded_file_name, process_audio=True)

            cleaned_data.pop('submit', None)  # remove submit field from list
            cleaned_data.pop('file', None)
            cleaned_data.pop('contenttrack_id', None)

            cleaned_data['uri'] = uri
            content_uploads = ContentUploads(**cleaned_data)  # create new object from data

            db.session.add(content_uploads)
            db.session.commit()

            flash(_('Content added.'), 'success')

        else:
            flash(_(form.errors.items()), 'error')

    return render_template('content/content_upload.html', content_uploads=content_uploads, form=form)


@content.route('/tracks/<int:track_id>/reorder/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def medias_reorder(**kwargs):
    str_indexes = request.form['indexes']
    indexes = str_indexes.split(',')
    indexes = map(int, indexes)
    i = 1
    for idx in indexes:
        music = ContentUploads.query.filter_by(id=idx).first_or_404()
        music.order = i
        i += 1
        db.session.add(music)
    db.session.commit()
    return str(indexes)


@content.route('/tracks/<int:track_id>/files/delete/<int:file_id>', methods=['GET'])
@login_required
@csrf.exempt
def track_files_delete(track_id, file_id):
    track = ContentTrack.query.filter_by(id=track_id).first_or_404()
    target = ContentUploads.query.filter_by(id=file_id).first_or_404()

    target.deleted = True

    try:
        db.session.add(target)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/hosts/')
@login_required
def list_hosts():
    hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).filter(
        User.id == current_user.id).all()
    return render_template('content/content_hosts.html', hosts=hosts)


@content.route('/hosts/add/', methods=['GET', 'POST'])
@login_required
def hosts_add():
    form = PersonForm(request.form)
    try:
        del form.created_at
        del form.updated_at
        del form.role
        del form.title
        del form.additionalcontact
        del form.privacy_code
        del form.network_id
    except AttributeError:
        pass

    host = None
    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('phone_inline')
        host = Person(**cleaned_data)  # create new object from data
        db.session.add(host)
        db.session.commit()
        flash(_('Host added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
    return render_template('content/content_host.html', host=host, form=form)


@content.route('/hosts/<int:host_id>/', methods=['GET', 'POST'])
@login_required
def host_edit(host_id):
    host = Person.query.filter(Person.id == host_id).first()
    form = PersonForm(obj=host)
    try:
        del form.created_at  # TODO: Include this and look at implications
        del form.updated_at  # TODO: Include this and look at implications
        del form.role
        del form.title
        del form.additionalcontact
        del form.privacy_code
        del form.network_id  # TODO: actually include this. A host can be used by multiple stations in a network
    except AttributeError:
        pass

    if form.validate_on_submit():
        form.populate_obj(host)
        db.session.add(host)
        db.session.commit()
        flash(_('Host edited.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
    return render_template('content/content_host.html', host=host, form=form)


@content.route('/hosts/<int:host_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def host_delete(host_id):
    host = Person.query.filter(Person.id == host_id).first()

    host.deleted = True

    try:
        db.session.add(host)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/community_content/', methods=['GET', 'POST'])
@login_required
def community_content():
    community_contents = CommunityContent.query.join(Station).join(Network).join(User, Network.networkusers).filter(
        User.id == current_user.id).all()
    return render_template('content/community_content.html', community_contents=community_contents)


@content.route('/community_content/<int:community_content_id>/<string:state>', methods=['GET'])
@login_required
@csrf.exempt
def community_content_toggle(community_content_id, state):
    community_content = CommunityContent.query.filter_by(id=community_content_id).first_or_404()

    if state == 'enable':
        community_content.approved = True
    else:
        community_content.approved = False

    try:
        db.session.add(community_content)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/podcasts/')
@login_required
def list_content_podcasts():
    # Podcasts in my network
    content_podcasts = ContentPodcast.query.all()
    return render_template('content/content_podcasts.html', content_podcasts=content_podcasts)


@content.route('/podcasts/<int:content_podcast_id>', methods=['GET', 'POST'])
@login_required
def content_podcast_definition(content_podcast_id):
    content_podcast = ContentPodcast.query.filter_by(id=content_podcast_id).first_or_404()
    form = ContentPodcastForm(obj=content_podcast, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_podcast)

        db.session.add(content_podcast)
        db.session.commit()
        flash(_('Podcast updated'), 'success')
    return render_template('content/content_podcast.html', content_podcast=content_podcast, form=form)


@content.route('/podcasts/<int:content_podcast_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def content_podcast_delete(content_podcast_id):
    content_podcast = ContentPodcast.query.filter_by(id=content_podcast_id).first_or_404()

    content_podcast.deleted = True

    try:
        db.session.add(content_podcast)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/podcasts/add/', methods=['GET', 'POST'])
@login_required
def content_podcast_add():
    form = ContentPodcastForm(request.form)
    content_podcast = None
    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy

        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data['created_by'] = current_user.id

        content_podcast = ContentPodcast(**cleaned_data)  # create new object from data

        db.session.add(content_podcast)
        db.session.commit()

        flash(_('Podcast added.'), 'success')
    elif request.method == "POST":
        flash(_(form.errors.items()), 'error')

    return render_template('content/content_podcast.html', content_podcast=content_podcast, form=form)


@content.route('/streams/')
@login_required
def list_content_streams():
    # streams in my network
    content_streams = ContentStream.query.all()
    return render_template('content/content_streams.html', content_streams=content_streams)


@content.route('/streams/<int:content_stream_id>', methods=['GET', 'POST'])
@login_required
def content_stream_definition(content_stream_id):
    content_stream = ContentStream.query.filter_by(id=content_stream_id).first_or_404()
    form = ContentStreamForm(obj=content_stream, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_stream)

        db.session.add(content_stream)
        db.session.commit()
        flash(_('Stream updated'), 'success')
    return render_template('content/content_stream.html', content_stream=content_stream, form=form)


@content.route('/streams/<int:content_stream_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def content_stream_delete(content_stream_id):
    content_stream = ContentStream.query.filter_by(id=content_stream_id).first_or_404()

    content_stream.deleted = True

    try:
        db.session.add(content_stream)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@content.route('/streams/add/', methods=['GET', 'POST'])
@login_required
def content_stream_add():
    form = ContentStreamForm(request.form)
    content_stream = None
    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy

        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data['created_by'] = current_user.id

        content_stream = ContentStream(**cleaned_data)  # create new object from data

        db.session.add(content_stream)
        db.session.commit()

        flash(_('Stream added.'), 'success')
    elif request.method == "POST":
        flash(_(form.errors.items()), 'error')

    return render_template('content/content_stream.html', content_stream=content_stream, form=form)


@content.route('/playlist/')
@login_required
def content_music_playlists():
    playlists_query = 'select content_musicplaylist.id, content_musicplaylist.title "playlist", ' \
                      'content_musicplaylist.description "description", radio_station.name "station", ' \
                      '(select count(*) from content_musicplaylistitem where playlist_item_type_id = 1 and ' \
                      'content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "songs", ' \
                      '(select count(*) from content_musicplaylistitem where playlist_item_type_id = 2 and ' \
                      'content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "albums", ' \
                      '(select count(*) from content_musicplaylistitem where playlist_item_type_id = 3 and ' \
                      'content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "artists" ' \
                      'from content_musicplaylist join radio_station on content_musicplaylist.station_id = ' \
                      'radio_station.id join radio_network on radio_station.network_id = radio_network.id join ' \
                      'radio_networkusers on radio_network.id = radio_networkusers.network_id join user_user on ' \
                      'radio_networkusers.user_id = user_user.id where user_user.id = :user_id and deleted is not true'
    params = {'user_id': current_user.id}
    content_musicplaylists = db.session.execute(playlists_query, params)
    return render_template('content/content_playlists.html', content_musicplaylists=content_musicplaylists)


@content.route('/playlist/<int:content_musicplaylist_id>', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_definition(content_musicplaylist_id):
    content_musicplaylist = ContentMusicPlaylist.query.filter_by(id=content_musicplaylist_id).first_or_404()
    form = ContentMusicPlaylistForm(obj=content_musicplaylist, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_musicplaylist)

        db.session.add(content_musicplaylist)
        db.session.commit()
        flash(_('Playlist updated.'), 'success')
    return render_template('content/content_playlist.html', content_musicplaylist=content_musicplaylist, form=form)


@content.route('/playlist/<int:playlist_id>/albums', methods=['GET', 'POST'])
@login_required
def list_content_musicplaylist_albums(playlist_id):
    columns = ["id", "item", "is_included", "songs"]
    sort_dir = "asc"
    if request.args['order[0][dir]'] in ["asc", "desc"]:
        sort_dir = request.args['order[0][dir]']
    albums_query = 'select content_musicalbum.id "id", content_musicalbum.title  "item", case when playlist.title ' \
                   'is not null then true else false end "is_included", (select count(*) from content_music where ' \
                   'album_id = content_musicalbum.id) "songs" from content_musicalbum left outer join (select * from ' \
                   'content_musicplaylistitem where playlist_item_type_id = 2 and not deleted and playlist_id = ' \
                   ':playlist_id) playlistitems on ' \
                   'content_musicalbum.id = playlistitems.playlist_item_id left outer join (select * from ' \
                   'content_musicplaylist where id = :playlist_id) playlist on playlistitems.playlist_id = ' \
                   'playlist.id  where content_musicalbum.station_id = (select station_id from content_musicplaylist ' \
                   'where id = :playlist_id) and content_musicalbum.title ' \
                   'ilike \'%\'||:search_term||\'%\' order by {0} {1}' \
        .format(columns[int(request.args['order[0][column]'])], sort_dir)

    content_musicplaylist_albums = db.session.execute(albums_query, {'playlist_id': playlist_id,
                                                                     'search_term': request.args['search[value]']})
    records = jquery_dt_paginator.get_records_from_query(content_musicplaylist_albums, request,
                                                         ["id", "item", "is_included", "songs"])
    return jsonify(records)

    # response = json.dumps([(dict(row.items())) for row in content_musicplaylist_albums])
    # return response


@content.route('/playlist/<int:playlist_id>/songs', methods=['GET', 'POST'])
@login_required
def list_content_musicplaylist_songs(playlist_id):
    columns = ["id", "item", "is_included", "songs"]
    sort_dir = "asc"
    if request.args['order[0][dir]'] in ["asc", "desc"]:
        sort_dir = request.args['order[0][dir]']
    songs_query = 'select content_music.id "id", content_music.title  "item", case when playlist.title is not null ' \
                  'then true else false end "is_included", (content_music.duration/1000)/60||\':\'||' \
                  '(content_music.duration/1000)%60 "songs" from content_music left outer join (select * from ' \
                  'content_musicplaylistitem where playlist_item_type_id = 1 and not deleted and playlist_id = ' \
                  ':playlist_id) playlistitems on ' \
                  'content_music.id = playlistitems.playlist_item_id left outer join (select * from ' \
                  'content_musicplaylist where  id = :playlist_id) playlist on playlistitems.playlist_id = ' \
                  'playlist.id where content_music.station_id = (select station_id from content_musicplaylist ' \
                  'where id = :playlist_id) and content_music.title ilike \'%\'||:search_term||\'%\' order by {0} {1}'.format(
        columns[int(request.args['order[0][column]'])], sort_dir)

    content_musicplaylist_songs = db.session.execute(songs_query, {'playlist_id': playlist_id,
                                                                   'search_term': request.args['search[value]']})
    records = jquery_dt_paginator.get_records_from_query(content_musicplaylist_songs, request, columns)
    return jsonify(records)


@content.route('/playlist/<int:playlist_id>/artists', methods=['GET', 'POST'])
@login_required
def list_content_musicplaylist_artists(playlist_id):
    columns = ["id", "item", "is_included", "songs"]
    sort_dir = "asc"
    if request.args['order[0][dir]'] in ["asc", "desc"]:
        sort_dir = request.args['order[0][dir]']
    artists_query = 'select content_musicartist.id "id", content_musicartist.title  "item", case when playlist.title ' \
                    'is not null then true else false end "is_included", (select count(*) from ' \
                    'content_music where artist_id = content_musicartist.id) "songs" from ' \
                    'content_musicartist left outer join (select * from content_musicplaylistitem where ' \
                    'playlist_item_type_id = 3 and not deleted and playlist_id = ' \
                    ':playlist_id) playlistitems on content_musicartist.id = ' \
                    'playlistitems.playlist_item_id left outer join (select * from content_musicplaylist where ' \
                    'id = :playlist_id) playlist on playlistitems.playlist_id = playlist.id  where ' \
                    'content_musicartist.station_id = (select station_id from content_musicplaylist ' \
                    'where id = :playlist_id) and content_musicartist.title ilike \'%\'||:search_term||\'%\' order by ' \
                    '{0} {1}'.format(
        columns[int(request.args['order[0][column]'])], sort_dir)

    content_musicplaylist_artists = db.session.execute(artists_query, {'playlist_id': playlist_id,
                                                                       'search_term': request.args['search[value]']})
    records = jquery_dt_paginator.get_records_from_query(content_musicplaylist_artists, request,
                                                         ["id", "item", "is_included", "songs"])
    return jsonify(records)

    # response = json.dumps([(dict(row.items())) for row in content_musicplaylist_artists])
    # return response


@content.route('/playlist/<int:playlist_id>/action', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_action(playlist_id):
    content_musicplaylist_songs = ContentMusicPlaylist.query.filter_by(id=playlist_id).all()
    return content_musicplaylist_songs


@content.route('/playlist/add/', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_add():
    form = ContentMusicPlaylistForm(request.form)
    content_musicplaylist = None
    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy

        cleaned_data.pop('submit', None)  # remove submit field from list
        content_musicplaylist = ContentMusicPlaylist(**cleaned_data)  # create new object from data

        db.session.add(content_musicplaylist)
        db.session.commit()

        flash(_('Playlist added.'), 'success')
    elif request.method == "POST":
        flash(_(form.errors.items()), 'error')

    return render_template('content/content_playlist.html', content_musicplaylist=content_musicplaylist, form=form)


@content.route('/playlist/<int:playlist_id>/add/<string:item_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_add_item(playlist_id, item_type, item_id):
    types = {"songs": 1, "albums": 2, "artists": 3}
    dt = dict()
    dt['playlist_id'] = playlist_id
    dt['playlist_item_id'] = item_id
    dt['playlist_item_type_id'] = types[item_type]
    dt['deleted'] = False
    tb = ContentMusicPlaylistItem(**dt)
    db.session.add(tb)
    db.session.commit()

    return '{"result": "ok" }'


@content.route('/playlist/<int:playlist_id>/remove/<string:item_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_remove_item(playlist_id, item_type, item_id):
    types = {"songs": 1, "albums": 2, "artists": 3}
    cmplis = ContentMusicPlaylistItem.query.filter(ContentMusicPlaylistItem.playlist_id == playlist_id).filter(
        ContentMusicPlaylistItem.playlist_item_type_id == types[item_type]).filter(
        ContentMusicPlaylistItem.playlist_item_id == item_id).all()
    for cmpli in cmplis:
        cmpli.deleted = True
        db.session.add(cmpli)
    db.session.commit()

    return '{"result": "ok" }'


@content.route('/playlist/<int:content_musicplaylist_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def content_musicplaylist_delete(content_musicplaylist_id):
    content_musicplaylist = ContentMusicPlaylist.query.filter_by(id=content_musicplaylist_id).first_or_404()

    content_musicplaylist.deleted = True

    try:
        db.session.add(content_musicplaylist)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'

# TODO: Try-catch all DB commits, as sometimes these fail and result in app failure unless rolled back
