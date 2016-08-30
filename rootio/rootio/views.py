# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash
from flask.ext.login import login_required

from ..extensions import db
from ..decorators import admin_required

from ..user import User
from ..user.forms import UserForm

from ..radio import Language, ProgramType, ContentType
from ..radio.forms import LanguageForm, ProgramTypeForm, ContentTypeForm

rootio = Blueprint('rootio', __name__, url_prefix='/rootio')

@rootio.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('rootio/index.html', users=users, active='index')


@rootio.route('/user/')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('rootio/users.html', users=users, active='users')


@rootio.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        flash('User updated.', 'success')

    return render_template('rootio/user.html', user=user, form=form)


@rootio.route('/language/')
@login_required
@admin_required
def languages():
    languages = Language.query.all()
    return render_template('rootio/languages.html', languages=languages, active='languages')


@rootio.route('/language/<int:language_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def language(language_id):
    language = Language.query.filter_by(id=language_id).first_or_404()
    form = LanguageForm(obj=language, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(language)

        db.session.add(language)
        db.session.commit()

        flash('Language updated.', 'success')

    return render_template('rootio/language.html', language=language, form=form)


@rootio.route('/language/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def language_add():
    form = LanguageForm(request.form)
    language = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        language = Language(**cleaned_data) #create new object from data
        
        db.session.add(language)
        db.session.commit()
        flash('Language added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('rootio/language.html', language=language, form=form)


@rootio.route('/program_type/')
@login_required
@admin_required
def program_types():
    program_types = ProgramType.query.all()
    return render_template('rootio/program_types.html', program_types=program_types, active='program_types')

@rootio.route('/program_type/<int:program_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def program_type(program_type_id):
    program_type = ProgramType.query.filter_by(id=program_type_id).first_or_404()
    form = ProgramTypeForm(obj=program_type, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(program_type)

        db.session.add(program_type)
        db.session.commit()

        flash('Program Type updated.', 'success')

    return render_template('rootio/program_type.html', program_type=program_type, form=form)


@rootio.route('/program_type/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def program_type_add():
    form = ProgramTypeForm(request.form)
    program_type = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        program_type = ProgramType(**cleaned_data) #create new object from data
        
        db.session.add(program_type)
        db.session.commit()
        flash('Program Type added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('rootio/program_type.html', program_type=program_type, form=form)

#TODO: program_type_add, with custom widget for picklefield

#added by nuno
@rootio.route('/content_type/')
@login_required
@admin_required
def content_types():
    content_types = ContentType.query.all()
    return render_template('rootio/content_types.html', content_types=content_types, active='content_types')

@rootio.route('/content_type/<int:content_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def content_type(content_type_id):
    content_types = ContentType.query.filter_by(id=content_type_id).first_or_404()
    form = ContentTypeForm(obj=content_types, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(content_types)

        db.session.add(content_types)
        db.session.commit()

        flash('Content Type updated.', 'success')

    return render_template('rootio/content_type.html', content_type=content_types, form=form)


@rootio.route('/content_type/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def content_type_add():
    form = ContentTypeForm(request.form)
    content_types = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        content_types = ContentType(**cleaned_data) #create new object from data
        
        db.session.add(content_types)
        db.session.commit()
        flash('Content Type added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('rootio/content_type.html', content_type=content_types, form=form)
