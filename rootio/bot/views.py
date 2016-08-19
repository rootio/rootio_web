from flask import Blueprint, render_template

from .aggregation_bot import __getRTP_RSS
from ..utils_bot import updateNextRun

#TODO GIVE A THREATMENT TO ALL THE STRING THAT ARE FETCHED BY THE BOT
#TODO ADD DECORATOR TO REFUSED CONNECTION FROM OUTSIDE OF THE SERVER.

bot = Blueprint('bot', __name__, url_prefix='/bot')

@bot.route('/rtp/<int:radio_id>&<int:function_id>',methods=['GET', 'POST'])
def rtp_puller(radio_id, function_id):
    __getRTP_RSS(radio_id,function_id)
    updateNextRun(radio_id, function_id, "active")
    return render_template("bot/getnews.html")


@bot.route('/fb/<int:radio_id>&<int:function_id>')
def facebook_puller(radio_id, function_id):
    print "facebook_bot"