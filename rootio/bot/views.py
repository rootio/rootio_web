import pytz
from flask import Blueprint, render_template, jsonify, request
from flask import Blueprint, render_template, request, flash, json,url_for
from flask.ext.babel import gettext as _

from flask.ext.login import login_required
from flask import Blueprint, render_template, request, flash, json,url_for

from rootio.bot.feedFBBot import getFBPosts
from rootio.radio import StationhasBots, Bothasinfo
from rootio.utils_bot import updateNBRun
from .aggregation_bot import __getRTP_RSS, textToDatetime
from ..extensions import db
from ..utils_bot import send_mail
from .models import ChatBotCmd
from ..radio.models import BotFunctions
from .forms import AddBotFunction, AddNewCommand

#TODO GIVE A THREATMENT TO ALL THE STRING THAT ARE FETCHED BY THE BOT
#TODO ADD DECORATOR TO REFUSED CONNECTION FROM OUTSIDE OF THE SERVER.

bot = Blueprint('bot', __name__, url_prefix='/bot')

@bot.route('/rtp/<int:radio_id>&<int:function_id>',methods=['GET', 'POST'])
def rtp_puller(radio_id, function_id):
    __getRTP_RSS(radio_id,function_id)
    #Update Time
    getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == radio_id,StationhasBots.fk_bot_function_id == function_id).first()
    #date = textToDatetime(str(updateNBRun(radio_id, function_id)), "%Y-%m-%d %H:%M:%S")
    date = updateNBRun(radio_id, function_id)
    #print "This is the date I'm printing " + str(date)
    getBot.next_run = date.replace(tzinfo=pytz.utc)
    try:
        db.session.add(getBot)
        db.session.commit()
        send_mail("AUTOMODE: I'm ok", " Hi it's me RTP-M RSS aggregator Just to let you know that I just run and it's everything ok. ;) \n Just to let you know I will be running at "+str(date.replace(tzinfo=pytz.utc)))
    except Exception as e:
	send_mail("AUTOMODE: Error updating next run data", str(e))

    return render_template("bot/getnews.html")


@bot.route('/fb/<int:radio_id>&<int:function_id>')
def facebook_puller(radio_id, function_id):
    #Get the facebook posts.
    getFBPosts(radio_id,function_id)

    getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == radio_id,StationhasBots.fk_bot_function_id == function_id).first()
    #date = textToDatetime(str(updateNBRun(radio_id, function_id)), "%Y-%m-%d %H:%M:%S")
    date = updateNBRun(radio_id, function_id)
    #print "This is the date I'm printing " + str(date)
    getBot.next_run = date.replace(tzinfo=pytz.utc)
    try:
        db.session.add(getBot)
        db.session.commit()
        send_mail("AUTOMODE: I'm ok", " Hi it's me Facebook Aggregator Bot Just to let you know that I just run and it's everything ok. ;) \n Just to let you know I will be running at "+str(date.replace(tzinfo=pytz.utc)))
    except Exception as e:
        send_mail("AUTOMODE: Error updating next run data", str(e))

    return render_template("bot/getnews.html")


@bot.route('/savechat', methods=['POST'])
def chatBot_Save():
    getanswer = ChatBotCmd.answerTocode(request.form['msg'])
    if getanswer:
        return getanswer.answer
    else:
        return "I don't know that command, check if you spelled it in the right way. " \
               "If you don't know which commands to use type help"


@bot.route('/add/function', methods=['GET', 'POST'])
@login_required
def add_aggregator_function():
    form = AddBotFunction(request.form)
    new_function = None

    if form.validate_on_submit():
        cleaned_data = form.data                        # make a copy
        cleaned_data.pop('submit', None)                # remove submit field from list
        new_function = BotFunctions(**cleaned_data)   # create new object from data
        try:
            db.session.add(new_function)
            db.session.commit()
            flash(_('New Aggregation.'), 'success')
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            flash(_('Error Bot Not Added.'), 'error')

    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('bot/aggregator_functions.html', new_function=new_function, form=form)

@bot.route('/add/command', methods=['GET', 'POST'])
@login_required
def add_chatbot_command():
    form = AddNewCommand(request.form)
    new_command = None

    if form.validate_on_submit():
        cleaned_data = form.data                        # make a copy
        cleaned_data.pop('submit', None)                # remove submit field from list
        new_command = ChatBotCmd(**cleaned_data)        # create new object from data
        try:
            db.session.add(new_command)
            db.session.commit()
            flash(_('New Chat Bot Command Added.'), 'success')
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            flash(_('Error No ChatBot Command Added.'), 'error')

    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('bot/chatbot_commands.html', new_command=new_command, form=form)

@bot.route('/list', methods=['GET', 'POST'])
@login_required
def list_aggregators():
    bots = dict()

    for b in StationhasBots.query.all():
        id = str(b.fk_radio_station_id) +'_'+str(b.fk_bot_function_id)
        bots[id] = {'function_id':b.function_of_bots.id,'station_id':b.bot_belongs_to_station.id,'function_name':b.function_of_bots.name,
                         'station_name': b.bot_belongs_to_station.name}
    return json.jsonify(bots)

@bot.route('/getinfo', methods=['GET', 'POST'])
@login_required
def getInfo():
    info = dict()

    for i in Bothasinfo.query.filter_by(fk_station_has_bots_radio_station_id=request.form['station_id'],fk_station_has_bots_bot_function_id=request.form['function_id']):
        info[i.id] = i.info
    return json.jsonify(info)