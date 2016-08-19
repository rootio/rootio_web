
import string
import random
import os
import re

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
    print "Preparing to send mail"
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

def add_cron(station, bot_function, recurrence, url, state,action):
    """
    Adds cron job to www-data crontab
    These cron jobs will make automatic request to the local website and will make the bot fetch info at specific times.
    This uses python-crontab
    :param station:         -> Station id
    :param bot_function:    -> Bot Function name id
    :param recurrence:      -> Run Frequency of the bot
    :param url:             -> Local URL to make web request
    :param state:           -> The bot is active or inactive
    :return:
    """
    cron = CronTab(user=True)

    if(state == "active"):
        print "Adding Bot"
        job = cron.new(command="wget -O - \"" + url + str(station.id) + "&" + str(bot_function.id) + "\" >/dev/null ",comment=str(station.id)+" "+str(bot_function.id))

        if recurrence == "MIN":
            job.minute.every(2)
        elif recurrence == "HOUR":
            job.minute.on(0)
            job.hour.during(0, 23)
        elif recurrence == "DAY":
            job.minute.on(0)
            job.hour.on(0)
        elif recurrence == "WEEEk":
            job.minute.on(0)
            job.hour.on(0)
            job.dow.on(1)
        if action == "added":
            send_mail("REPORT: New bot addition", "A new Bot has been added \n" + "wget -O - \"" + url + str(station.id) + "&" + str(bot_function.id) + "\" >/dev/null # " + str(station.id)+" "+str(bot_function.id))
        else:
            send_mail("REPORT: Bot was enabled","The bot is now enabled.")
    else:
        cron.remove_all(comment=str(station.id) + " " + str(bot_function.id))
        if action == "added":
            send_mail("REPORT: New bot addition", "The was added to database no cronjob was created.")
        else:
            send_mail("REPORT: Bot was disabled", "The bot is now disabled.")
    cron.write()


def updateNextRun(station, bot_function, state):
    """
    Update next_run field that show the time in which the bot will run next time
    :return:
    """
    cron = CronTab(user=True)
    getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == station.id, StationhasBots.fk_bot_function_id == bot_function.id).first()
    if state == "active":
        try:
            list = cron.find_comment(str(station.id) + " " + str(bot_function.id))
            for i in list:
                schedule = i.schedule(date_from=datetime.now())
            getBot.next_run = schedule.get_next()
            db.session.add(getBot)
            db.session.commit()
        except Exception as e:
            db.session.roolback()
            print str(e)
    else:
        try:
            #getBot = StationhasBots.query.filter(StationhasBots.fk_radio_station_id == station.id , StationhasBots.fk_bot_function_id == bot_function.id).first()
            getBot.next_run = None
            db.session.add(getBot)
            db.session.commit()
        except Exception as e:
            db.session.roolback()
            print str(e)
