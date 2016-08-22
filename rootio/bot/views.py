import pytz
from flask import Blueprint, render_template

from rootio.bot.feedFBBot import getFBPosts
from rootio.radio import StationhasBots
from rootio.utils_bot import updateNBRun
from .aggregation_bot import __getRTP_RSS, textToDatetime
from ..extensions import db
from ..utils_bot import send_mail

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