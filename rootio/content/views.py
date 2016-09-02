# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _
from werkzeug.utils import secure_filename

from .models import ContentTrack, ContentUploads 
from .forms import ContentTrackForm, ContentUploadForm 

from ..extensions import db, csrf
from datetime import datetime

ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

content = Blueprint('content', __name__, url_prefix='/content')


@content.route('/')
@login_required
def index():
    #select ct.id, ct.name "track", rct.name "content type", count(*) "uploads" , (select count(*) from radio_program where structure like '%'||ct.description||'%') "subscriptions" from content_track as ct join radio_contenttype as rct on "ct".content_contenttypeid = rct.id join content_uploads as cu on ct.id = cu.contenttrack_id  group by ct.id, rct.name;

    return render_template('content/index.html')


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
@csrf.exempt
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
        cleaned_data.pop('file',None)  
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        cleaned_data['contenttrack_id'] = cleaned_data['contenttrack_id'].id

        uri = "{0}/{1}/{2}".format(str(current_user.id),str(cleaned_data['contenttrack_id']), save_uploaded_file(request.files['file'],os.path.join("/home/amour/test_media",str(current_user.id),str(cleaned_data['contenttrack_id']))))
             
        cleaned_data['uri'] = uri
        content_uploads = ContentUploads(**cleaned_data) #create new object from data

        db.session.add(content_uploads)
        db.session.commit()
        

        flash(_('Content added.'), 'success')
        
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_add.html', form=form) 


@content.route('/news/')
@login_required
def content_news():
    content_news = ContentUploads.query.filter_by(uploaded_by=current_user.id).all()#.filter_by(content_tracks.content_type.name='news').all()
    return render_template('content/content_news.html', content_news=content_news)


@content.route('/news/<int:content_news_id>', methods=['GET', 'POST'])
@login_required
def content_news_edit(content_news_id):
    content_news = ContentUploads.query.filter_by(id=content_news_id).first_or_404()
    form = ContentUploadForm(obj=content_news, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_news)

        db.session.add(content_news)
        db.session.commit()
        flash(_('Content updated.'), 'success')
    return render_template('content/content_news_edit.html', content_news=content_news, form=form)


@content.route('/news/add/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def content_news_add():
    form = ContentUploadForm(request.form)
    content_news = None
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
        cleaned_data['uploaded_by'] = current_user.id
        cleaned_data['name'] = filename
        cleaned_data['contenttrack_id'] = cleaned_data['contenttrack_id'].id

        uri = "{0}/{1}/{2}".format(str(current_user.id),str(cleaned_data['contenttrack_id']), save_uploaded_file(request.files['file'],os.path.join("/home/amour/test_media",str(current_user.id),str(cleaned_data['contenttrack_id']))))
             
        cleaned_data['uri'] = uri
        content_news = ContentUploads(**cleaned_data) #create new object from data

        db.session.add(content_news)
        db.session.commit()
        

        flash(_('Content added.'), 'success')
        
    elif request.method == "POST":
         flash(_(form.errors.items()),'error')
    
    return render_template('content/content_news_add.html', form=form)     