
import string
import random
import os
import re

import pytz
from crontab import CronTab
from bs4 import BeautifulSoup
from flask.ext.mail import Message
import httplib2
from .extensions import mail
from datetime import datetime
from .radio.models import StationhasBots
from .extensions import db



def getpage(url):
    """
    Changed but comes from https://github.com/nandopedrosa/as_mais_lidas
    Downloads the html page

    :rtype: tuple
    :param url: the page address
    :return: the header response and contents (bytes) of the page
    """
    http = httplib2.Http()
    response, content = http.request(url, headers={'User-agent': 'Mozilla/5.0'})
    return response, content

def parsepage(content, parsetype):
    """
    Changed but comes from https://github.com/nandopedrosa/as_mais_lidas
    Parses a single page and its contents into a BeautifulSoup object

    :param content: (bytearray)
    :return soup:   (object)
    """
    soup = BeautifulSoup(content,parsetype)
    return soup


def send_mail(title, body):
    """
    This function was made to receive errors that may make the bots stop their work while they're using cronjobs
    :param title: Something related with the error
    :param body: The error that happened
    :return:
    """
    print body   
    """print "Preparing to send mail"
    CONST_SENDERMAIL = "speechworks2016@gmail.com"
    recipient_mails = "fabiocl93@gmail.com"
    try:
        msg = Message(title,
                      sender=CONST_SENDERMAIL,
                      recipients=[recipient_mails])
        msg.body = body
        mail.send(msg)
        print 'Mail Sent'
    except Exception as e:
        print str(e)
        print "An error happened mail was not sent" 
    """

def add_cron(bot, type):
    """
    -> Adds cron jobs.
    :param bot:     (Object) Generate to submit the form that allow o change the bot
    :param type:    (String) Allow us to identify if we're adding or editing a bot
    :return:        (Object) Object with an updated fields
    """
    print "Prepare Cron"
    cron = CronTab(user=True)
    #cron.remove_all()
    if type == "add":
        print "Adding a new bot"
        if bot.state == "active":
           bot = bakeCron(bot,cron)
        else:
           bot = removeCron(bot,cron)
           print ("Added bot no cronjob has been created.")
    else:
        getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == bot.bot_belongs_to_station.id, StationhasBots.fk_bot_function_id == bot.function_of_bots.id).first()
        #list = cron.find_comment(str(bot.bot_belongs_to_station.id) + " " + str(bot.function_of_bots.id))
        print "Editing Bot"
        if getBot:
            if bot.state == "active":
                #Remove the existing
                bot = removeCron(bot,cron)
                #Add a new one
                bot = bakeCron(bot, cron)
                print "Added a cronjob for existing bot"
            else:
                bot = removeCron(bot,cron)
                print "Remove exiting cron Job"
        else:
            print "The bot does not exist and you're trying to edit it."
    #cron.write()
    return bot #ALways return the bot even if it has not been changed

def bakeCron(bot,cron):
    """
    -> Generates the cron job based on the user options
    :param bot:     (Object) Generate to submit the form that allow o change the bot
    :param cron:    (Object) Generated to manipulate cron jobs
    :return:        (Object) Object with an updated next_run field
    """
    print "Add new cron"
    job = cron.new(command="wget -O - \"" + bot.local_url + str(bot.bot_belongs_to_station.id) + "&" + str(bot.function_of_bots.id) + "\" >/dev/null ", comment=str(bot.bot_belongs_to_station.id) + " " + str(bot.function_of_bots.id))
    #print "Baking Cron"
    if bot.run_frequency == "MIN":
        job.minute.every(2)
    elif bot.run_frequency == "HOUR":
        job.minute.on(0)
        job.hour.during(0, 23)
    elif bot.run_frequency == "DAY":
        job.minute.on(0)
        job.hour.on(0)
    elif bot.run_frequency == "WEEEk":
        job.minute.on(0)
        job.hour.on(0)
        job.dow.on(1)
    cron.write()
    #print "Cron was baked"
    # print ("Added a cronjob for the new bot.")
    date = updateNBRun(bot.bot_belongs_to_station.id, bot.function_of_bots.id)
    bot.next_run = date.replace(tzinfo=pytz.utc)
    return bot

def updateNBRun(station,bot_function):
    """
    -> Updates the next run field based on the cronjob that has been added
    :param station:         (int) radio station id
    :param bot_function:    (int) bot function name id
    :return:                (datetime) to be added to the database
    """
    print "Update next run"
    cron = CronTab(user=True)
    list = cron.find_comment(str(station) + " " + str(bot_function))
    for i in list:
        schedule = i.schedule(date_from=datetime.now())
        #print schedule.get_next() #This may lead to a BUG time may be showned wrong
    return schedule.get_next()

def removeCron(bot,cron):
    """
    -> Removes existing cronjobs by their comment
    :param bot:     (Object) Generate to submit the form that allow o change the bot
    :param cron:    (Object) Generated to manipulate cron jobs
    :return:        (Object) Object with an updated next_run field
    """
    print "Removing Job"
    #print str(bot.bot_belongs_to_station.id) + " " + str(bot.function_of_bots.id)
    cron.remove_all(comment=str(bot.bot_belongs_to_station.id) + " " + str(bot.function_of_bots.id))
    cron.write()
    bot.next_run = None
    return bot

def validate_sms(message):
    message = message.replace("(", ",")
    message = message.replace(")", ",")  # removes the bug that makes FS send a bye signal do TTS server.
    message = message.replace("\n", " ")  # Remove the new line character people can envetually send and makes FS stop the TTS
    message = message.replace("\r"," ")  # Remove the new line character people can envetually send and makes FS stop the TTS
    message = message.replace('"', "")  # Remove the quotes
    message = message.replace("'", "")  # Remove the single quotes
    return message


