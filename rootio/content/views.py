# -*- coding: utf-8 -*-welcome_message_file = FileField('Welcome message')

import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, json
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _
from werkzeug.utils import secure_filename
from sqlalchemy import MetaData
from flask_paginate import Pagination

from ..radio.models import ContentType, Person, Network, Station
from ..user.models import User
from ..radio.forms import PersonForm
from ..config import DefaultConfig
from .models import ContentMusicPlaylistItem, ContentMusic, ContentMusicPlaylist, ContentMusicAlbum, ContentMusicArtist, ContentTrack, ContentUploads, ContentPodcast, ContentPodcastDownload, CommunityMenu, CommunityContent
from .forms import ContentMusicPlaylistForm, ContentTrackForm, ContentUploadForm, ContentPodcastForm, ContentNewsForm , ContentAddsForm, ContentStreamsForm, ContentMusicForm, CommunityMenuForm
from ..decorators import returns_json
from ..extensions import db, csrf
from datetime import datetime

ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

content = Blueprint('content', __name__, url_prefix='/content')


@content.route('/')
@login_required
def index():
    #re-write using ORM
    #Filter by network when Track contains network id, filter by uploader
    status_query = "select ct.id, ct.name \"track\", rct.name \"content type\", count(*) \"uploads\" , (select count(*) from radio_program where structure like '%'||ct.description||'%') \"subscriptions\" from content_track as ct join content_type as rct on \"ct\".type_id = rct.id join content_uploads as cu on ct.id = cu.track_id  group by ct.id, rct.name";
    content = db.session.execute(status_query)
    
    return render_template('content/index.html', content=content)


@content.route('/tracks/')
@login_required
def tracks():
    tracks = ContentTrack.query.filter_by(uploaded_by=current_user.id).all()
    return render_template('content/tracks.html', tracks=tracks, active='tracks')

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

        cleaned_data = form.data #make a copy
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data.pop('submit',None) #remove submit field from list
        tracks = ContentTrack(**cleaned_data) #create new object from data
        db.session.add(tracks)
        db.session.commit()
        flash(_('Track added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')
    return render_template('content/track.html', tracks=tracks, form=form)



@content.route('/uploads/')
@login_required
def content_uploads():
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


def save_uploaded_file(file, directory):
    datepart = datetime.now().strftime("%y%m%d%H%M%S")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file.save(os.path.join(directory,"{0}_{1}".format(datepart,file.filename)))
    return "{0}_{1}".format(datepart,file.filename)


@content.route('/uploads/add/', methods=['GET', 'POST'])
@login_required
def content_upload_add():
    form = ContentUploadForm(request.form)
    content_uploads = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list 
        cleaned_data.pop('file',None)  
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        cleaned_data['content_contenttypeid'] = cleaned_data['contenttrack_id'].content_contenttypeid
        cleaned_data['contenttrack_id'] = cleaned_data['contenttrack_id'].id

        uri = "{0}/{1}/{2}".format("media",str(cleaned_data['contenttrack_id']), save_uploaded_file(request.files['file'],os.path.join(DefaultConfig.CONTENT_DIR,str(current_user.id),str(cleaned_data['contenttrack_id']))))
             
        cleaned_data['uri'] = uri
        content_uploads = ContentUploads(**cleaned_data) #create new object from data
    
        db.session.add(content_uploads)
        db.session.commit()
        

        flash(_('Content added.'), 'success')
        
    elif request.method == "POST":
        flash(_(form.errors.items()),'error')
        
    return render_template('content/content_upload.html', content_uploads=content_uploads, form=form) 


@content.route('/news/', defaults={'page': 1})
@content.route('/news/')
@login_required
def content_news():
    name_content = 'News'
    page= request.args.get('page', type=int, default=1)
    per_page = 2
    content_type = ContentType.query.filter(ContentType.name=='News').first()
    content_news = ContentUploads.query.join(ContentTrack).filter(ContentUploads.uploaded_by==current_user.id).filter(ContentTrack.type_id==content_type.id) #.slice(0, per_page).all()

    pagination = Pagination(page=page, per_page=per_page, search='', total=5, record_name='records')
    return render_template('content/content_news.html', content_news=content_news.slice((page - 1) * per_page, per_page).all(), pagination=pagination, )
    #return render_template('content/content_news.html', content_news=content_news)


@content.route('/news/<int:content_news_id>', methods=['GET', 'POST'])
@login_required
def content_news_edit(content_news_id):
    content_news = ContentUploads.query.filter_by(id=content_news_id).first_or_404()
    form = ContentNewsForm(obj=content_news, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_news)

        db.session.add(content_news)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_news_edit.html', content_news=content_news, form=form)


@content.route('/news/add/', methods=['GET', 'POST'])
@login_required
def content_news_add():
    form = ContentNewsForm(request.form)
    content_news = None
    cleaned_data = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('file',None)
        cleaned_data.pop('submit',None) #remove submit field from list  
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        cleaned_data['track_id'] = cleaned_data['track_id'].id


        uri = "{0}/{1}/{2}".format("news",str(cleaned_data['track_id']), save_uploaded_file(request.files['file'],os.path.join(DefaultConfig.CONTENT_DIR,"news",str(cleaned_data['track_id']))))
             
        cleaned_data['uri'] = uri
        content_news = ContentUploads(**cleaned_data) #create new object from data
       
        db.session.add(content_news)
        db.session.commit()
        

        flash(_('Content added.'), 'success')  
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_news_edit.html', form=form)   


@content.route('/ads/')
@login_required
def content_ads():
    content_type = ContentType.query.filter(ContentType.name=='Advertisements').first()
    ads = ContentUploads.query.join(ContentTrack).filter(ContentUploads.uploaded_by==current_user.id).filter(ContentTrack.type_id==content_type.id).all()
    return render_template('content/content_ads.html', ads=ads)  


@content.route('/ads/<int:ad_id>', methods=['GET', 'POST'])
@login_required
def content_ads_edit(ad_id):
    ad = ContentUploads.query.filter_by(id=ad_id).first_or_404()
    form = ContentAddsForm(obj=ad, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(ad)

        db.session.add(ad)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_ads_edit.html', ad=ad, form=form)

DefaultConfig.CONTENT_DIR
@content.route('/ads/add/', methods=['GET', 'POST'])
@login_required
def content_ads_add():
    form = ContentAddsForm(request.form)
    content_adds = None
    cleaned_data = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not file or not allowed_file(file.filename):
            flash('Invalid file format')
            return redirect(request.url)   
    if form.validate_on_submit():
        filename = secure_filename(file.filename)
        cleaned_data = form.data #make a copy
        cleaned_data.pop('file',None)
        cleaned_data.pop('submit',None) #remove submit field from list  
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        #cleaned_data['content_contenttypeid'] = cleaned_data['track_id'].content_contenttypeid
        cleaned_data['track_id'] = cleaned_data['track_id'].id


        uri = "{0}/{1}/{2}".format("ads",str(cleaned_data['track_id']), save_uploaded_file(request.files['file'],os.path.join(DefaultConfig.CONTENT_DIR,"ads", str(cleaned_data['track_id']))))
             
        cleaned_data['uri'] = uri
        content_adds = ContentUploads(**cleaned_data) #create new object from data
       
        db.session.add(content_adds)
        db.session.commit()
        

        flash(_('Advertisement uploaded.'), 'success')  
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_ads_edit.html', form=form) 

@content.route('/streams/')
@login_required
def content_streams():
    content_type = ContentType.query.filter(ContentType.name=='Streams').first()
    content_streams = ContentUploads.query.join(ContentTrack).filter(ContentUploads.uploaded_by==current_user.id).filter(ContentTrack.type_id==content_type.id).all()
    return render_template('content/content_streams.html', content_streams=content_streams) 


@content.route('/streams/<int:content_streams_id>', methods=['GET', 'POST'])
@login_required
def content_stream(content_streams_id):
    content_stream = ContentUploads.query.filter_by(id=content_streams_id).first_or_404()
    form = ContentStreamsForm(obj=content_stream, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_stream)
        
        db.session.add(content_stream)
        db.session.commit()
        flash(_('Stream updated'), 'success')
    return render_template('content/content_stream.html', content_streams=content_stream, form=form)


@content.route('/streams/add/', methods=['GET', 'POST'])
@login_required
def content_streams_add():
    form = ContentStreamsForm(request.form)
    content_streams = None
    cleaned_data = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('file',None)

        cleaned_data.pop('submit',None) #remove submit field from list  
        cleaned_data['uploaded_by'] = current_user.id
        #cleaned_data['name'] = filename
        #cleaned_data['content_contenttypeid'] = cleaned_data['contenttrack_id'].content_contenttypeid
        #cleaned_data['track_id'] = cleaned_data['track_id'].id

        content_streams = ContentUploads(**cleaned_data) #create new object from data
       
        db.session.add(content_streams)
        db.session.commit()
        
        flash(_('Content added.'), 'success')  
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_stream.html', form=form) 


@content.route('/medias/')
@login_required
def content_medias():
    content_type = ContentType.query.filter(ContentType.name=='Media').first()
    medias = ContentUploads.query.join(ContentTrack).filter(ContentUploads.uploaded_by==current_user.id).filter(ContentTrack.type_id==content_type.id).order_by(ContentUploads.order).all()
    return render_template('content/content_medias.html', medias=medias)


@content.route('/medias/<int:content_media_id>', methods=['GET', 'POST'])
@login_required
def content_media(content_media_id):
    content_media = ContentUploads.query.filter_by(id=content_news_id).first_or_404()
    form = ContentMusicForm(obj=content_media, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_media)

        db.session.add(content_media)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_media.html', content_media=content_media, form=form)


@content.route('/medias/add/', methods=['GET', 'POST'])
@login_required
def content_medias_add():
    form = ContentMusicForm(request.form)
    content_media = None
    cleaned_data = None
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('file',None)
        cleaned_data.pop('submit',None) #remove submit field from list  
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        #cleaned_data['type_id'] = cleaned_data['track_id'].content_contenttypeid
        #Fix this - Form should automatically go into db
        cleaned_data['track_id'] = cleaned_data['track_id'].id
   

        uri = "{0}/{1}/{2}".format("media",str(cleaned_data['track_id']), save_uploaded_file(request.files['file'],os.path.join(DefaultConfig.CONTENT_DIR,"media",str(cleaned_data['track_id']))))

        cleaned_data['uri'] = uri
        content_media = ContentUploads(**cleaned_data) #create new object from data
       
        db.session.add(content_media)
        db.session.commit()
        

        flash(_('Media Uploaded'), 'success')  
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_media.html', form=form)  


@content.route('/medias/reorder/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def medias_reorder():
    str_indexes = request.form['indexes']
    indexes = str_indexes.split(',')
    indexes = map(int,indexes)
    i = 1
    for index in indexes:
        music = ContentUploads.query.filter_by(id=index).first_or_404()
        music.order = i
        i +=1
        db.session.add(music)
    db.session.commit()
    flash(_('Media reordered.'), 'success')   
    return str(indexes)  

@content.route('/ads/reorder/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def ads_reorder():
    str_indexes = request.form['indexes']
    indexes = str_indexes.split(',')
    indexes = map(int,indexes)
    i = 1
    for index in indexes:
        adds = ContentUploads.query.filter_by(id=index).first_or_404()
        adds.order = i
        i +=1
        db.session.add(adds)
    db.session.commit()
    flash(_('Ads reordered.'), 'success')  
    return str(indexes)  


@content.route('/hosts/')
@login_required
def hosts():
    hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('content/content_hosts.html', hosts=hosts)

@content.route('/hosts/add/', methods=['GET', 'POST'] )
@login_required
def hosts_add():
    form = PersonForm(request.form)
    del form.created_at
    del form.updated_at
    del form.role
    del form.title
    del form.additionalcontact
    del form.privacy_code

    host = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        cleaned_data.pop('phone_inline')
        host = Person(**cleaned_data) #create new object from data
        db.session.add(host)
        db.session.commit()
        flash(_('Host added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'),'error')
    return render_template('content/content_host.html', host=host, form=form)

@content.route('/hosts/<int:host_id>/', methods=['GET', 'POST'] )
@login_required
def host_edit(host_id):
    host = Person.query.filter(Person.id==host_id).first()
    form = PersonForm(obj=host)
    del form.created_at
    del form.updated_at
    del form.role
    del form.title
    del form.additionalcontact
    del form.privacy_code

    if form.validate_on_submit():
        form.populate_obj(host)
        cleaned_data = form.data #make a copy
        #cleaned_data.pop('submit',None) #remove submit field from list
        #cleaned_data.pop('phone_inline')
        #host = Person(**cleaned_data) #create new object from data
        db.session.add(host)
        db.session.commit()
        flash(_('Host edited.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'),'error')
    return render_template('content/content_host.html', host=host, form=form)


@content.route('/community_content/', methods=['GET', 'POST'] )
@login_required
def community_content():
    community_contents = CommunityContent.query.join(Station).join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('content/community_content.html', community_contents=community_contents)

@content.route('/community_menu', methods=['GET', 'POST'] )
@login_required
def community_menu():
    form = CommunityMenuForm(request.form)
    community_menu = None
    if request.method == 'POST':
       pass #validate files here
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) 
        for key in request.files.keys():
            prompt_file = request.files[key]
            filepath = save_uploaded_file(prompt_file,os.path.join(DefaultConfig.CONTENT_DIR, "community-menu", request.form['station']))
            cleaned_data[key] = "{0}/{1}/{2}".format("community-menu",request.form['station'], filepath)
            
        community_menu = CommunityMenu(**cleaned_data) #create new object from data

        db.session.add(community_menu)
        db.session.commit()


        flash(_('Configuration saved.'), 'success')

    elif request.method == "POST":
        flash(_(form.errors.items()),'error')

    return render_template('content/community_menu.html', community_menu=community_menu, form=form)

@content.route('/podcasts/')
@login_required
def content_podcasts():
    #Podcasts in my network
    content_podcasts = ContentPodcast.query.all()
    return render_template('content/content_podcasts.html', content_podcasts=content_podcasts)


@content.route('/podcasts/<int:content_podcast_id>', methods=['GET', 'POST'])
@login_required
def content_podcast(content_podcast_id):
    content_podcast = ContentPodcast.query.filter_by(id=content_podcast_id).first_or_404()
    form = ContentPodcastForm(obj=content_podcast, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_podcast)

        db.session.add(content_podcast)
        db.session.commit()
        flash(_('Podcast updated'), 'success')
    return render_template('content/content_podcast.html', content_podcast=content_podcast, form=form)


@content.route('/podcasts/add/', methods=['GET', 'POST'])
@login_required
def content_podcast_add():
    form = ContentPodcastForm(request.form)
    content_podcast = None
    cleaned_data = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy

        cleaned_data.pop('submit',None) #remove submit field from list  
        cleaned_data['created_by'] = current_user.id

        content_podcast = ContentPodcast(**cleaned_data) #create new object from data

        db.session.add(content_podcast)
        db.session.commit()

        flash(_('Podcast added.'), 'success')
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')

    return render_template('content/content_podcast.html', form=form)

@content.route('/playlist/')
@login_required
def content_musicplaylists():
    playlists_query = 'select content_musicplaylist.id, content_musicplaylist.title "playlist",content_musicplaylist.description "description", radio_station.name "station", (select count(*) from content_musicplaylistitem where playlist_item_type_id = 1 and content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "songs", (select count(*) from content_musicplaylistitem where playlist_item_type_id = 2 and content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "albums", (select count(*) from content_musicplaylistitem where playlist_item_type_id = 3 and content_musicplaylistitem.playlist_id = content_musicplaylist.id and not deleted) "artists" from content_musicplaylist join radio_station on content_musicplaylist.station_id = radio_station.id join radio_network on radio_station.network_id = radio_network.id join radio_networkusers on radio_network.id = radio_networkusers.network_id join user_user on radio_networkusers.user_id = user_user.id where user_user.id = :user_id'
    params = { 'user_id':current_user.id }
    content_musicplaylists = db.session.execute(playlists_query, params)
    return render_template('content/content_playlists.html', content_musicplaylists=content_musicplaylists)


@content.route('/playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def content_musicplaylist(playlist_id):
    content_musicplaylist = ContentMusicPlaylist.query.filter_by(id=playlist_id).first_or_404()
    form = None #ContentMusicPlaylistForm(obj=content_musicplaylist, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_musicplaylist)

        db.session.add(content_musicplaylist)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_musicplaylist.html', content_musicplaylist=content_musicplaylist, form=form)


@content.route('/playlist/<int:playlist_id>/albums', methods=['GET', 'POST'])
@login_required
@returns_json
def content_musicplaylist_albums(playlist_id):
    albums_query = 'select content_musicalbum.id "id", content_musicalbum.title  "item", (select count(*) from content_music where album_id = content_musicalbum.id) "songs", playlist.title "playlist", case when playlist.title is not null then true else false end "is_included" from content_musicalbum left outer join (select * from content_musicplaylistitem where playlist_item_type_id = 2 and not deleted) playlistitems on content_musicalbum.id = playlistitems.playlist_item_id left outer join (select * from content_musicplaylist where id = :playlist_id) playlist on playlistitems.playlist_id = playlist.id'
    
    content_musicplaylist_albums = db.session.execute(albums_query, { 'playlist_id': playlist_id })
    response = json.dumps([(dict(row.items())) for row in content_musicplaylist_albums])    
    return response

@content.route('/playlist/<int:playlist_id>/songs', methods=['GET', 'POST'])
@login_required
@returns_json
def content_musicplaylist_songs(playlist_id):
    songs_query = 'select content_music.id "id", content_music.title  "item", playlist.title "playlist", case when playlist.title is not null then true else false end "is_included", (content_music.duration/1000)/60||\':\'||(content_music.duration/1000)%60 "songs" from content_music left outer join (select * from content_musicplaylistitem where playlist_item_type_id = 1 and not deleted) playlistitems on content_music.id = playlistitems.playlist_item_id left outer join (select * from content_musicplaylist where id = :playlist_id) playlist on playlistitems.playlist_id = playlist.id'

    content_musicplaylist_songs = db.session.execute(songs_query, { 'playlist_id': playlist_id })
    response = json.dumps([(dict(row.items())) for row in content_musicplaylist_songs])
    return response

@content.route('/playlist/<int:playlist_id>/artists', methods=['GET', 'POST'])
@login_required
@returns_json
def content_musicplaylist_artists(playlist_id):
    artists_query = 'select content_musicartist.id "id", content_musicartist.title  "item", (select count(*) from content_music_musicartist where artist_id = content_musicartist.id) "songs", playlist.title "playlist", case when playlist.title is not null then true else false end "is_included" from content_musicartist left outer join (select * from content_musicplaylistitem where playlist_item_type_id = 3 and not deleted) playlistitems on content_musicartist.id = playlistitems.playlist_item_id left outer join (select * from content_musicplaylist where id = :playlist_id) playlist on playlistitems.playlist_id = playlist.id'

    content_musicplaylist_artists = db.session.execute(artists_query, { 'playlist_id': playlist_id })
    response = json.dumps([(dict(row.items())) for row in content_musicplaylist_artists])
    return response

@content.route('/playlist/<int:playlist_id>/action', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_action(playlist_id):
    content_musicplaylist_songs = ContentMusicPlaylist.query.filter_by(id=playlist_id).all()
    return content_musicplaylist_albums

@content.route('/playlist/add/', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_add():
    form = ContentMusicPlaylistForm(request.form)
    content_musicplaylist = None
    cleaned_data = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy

        cleaned_data.pop('submit',None) #remove submit field from list  
        content_musicplaylist = ContentMusicPlaylist(**cleaned_data) #create new object from data

        db.session.add(content_musicplaylist)
        db.session.commit()

        flash(_('Playlist added.'), 'success')
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')

    return render_template('content/content_playlist.html', form=form)


@content.route('/playlist/<int:playlist_id>/add/<string:item_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def content_musicplaylist_add_item(playlist_id, item_type, item_id):
    types = { "songs":1,"albums":2, "artists":3 }
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
    types = { "songs":1,"albums":2, "artists":3 }
    cmplis = ContentMusicPlaylistItem.query.filter(ContentMusicPlaylistItem.playlist_id==playlist_id).filter(ContentMusicPlaylistItem.playlist_item_type_id==types[item_type]).filter(ContentMusicPlaylistItem.playlist_item_id==item_id).all()
    for cmpli in cmplis:
        cmpli.deleted = True
        db.session.add(cmpli)
    db.session.commit()

    return '{"result": "ok" }'
