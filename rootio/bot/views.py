from flask import Blueprint, render_template

from rootio.radio import StationhasBots
from rootio.utils_bot import updateNBRun
from .aggregation_bot import __getRTP_RSS
from ..extensions import db

#TODO GIVE A THREATMENT TO ALL THE STRING THAT ARE FETCHED BY THE BOT
#TODO ADD DECORATOR TO REFUSED CONNECTION FROM OUTSIDE OF THE SERVER.

bot = Blueprint('bot', __name__, url_prefix='/bot')

@bot.route('/rtp/<int:radio_id>&<int:function_id>',methods=['GET', 'POST'])
def rtp_puller(radio_id, function_id):
    __getRTP_RSS(radio_id,function_id)
    #Update Time
    getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == radio_id,StationhasBots.fk_bot_function_id == function_id).first()
    getBot.next_run = updateNBRun(radio_id, function_id)
    try:
        db.session.add(getBot)
        db.session.commit()
    except Exception as e:
        print e
    return render_template("bot/getnews.html")


@bot.route('/fb/<int:radio_id>&<int:function_id>')
def facebook_puller(radio_id, function_id):
    print "facebook_bot"