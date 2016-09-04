# -*- coding: utf-8 -*-
from datetime import datetime

from rootio.utils_bot import validate_sms

from rootio.radio.models import  Bothasinfo, StationhasBots

from rootio.extensions import db

from rootio.utils_bot import getpage, parsepage, send_mail

def __getRTP_RSS(station,function):
    """
    Gets news from RTP Madeira
    :param function: (int) -> id of the station
    :param station:  (int) -> id of the function
    :return:
    """

    url = StationhasBots.query.filter(StationhasBots.fk_radio_station_id==station,StationhasBots.fk_bot_function_id==function).first()
    date_format = "%a, %d %b %Y %H:%M:%S"

    response, content = getpage(url.source_url)
    soup = parsepage(content,'xml')

    hasRows = Bothasinfo.query.filter(Bothasinfo.fk_station_has_bots_bot_function_id == function, Bothasinfo.fk_station_has_bots_radio_station_id == station).count()
    for article in soup.findAll('item'):
        link_wtho_tag = unicode(article.find('link').get_text())

        ##Removing news that have player (video or audio)
        if "-video_" in link_wtho_tag or "-video-_" in link_wtho_tag or "-audio_" in link_wtho_tag or "-audio-_" in link_wtho_tag:
            print "Ignored article contains video or audio"
        else:
            #title = article.find('title').get_text()
            pub_date = textToDatetime(article.find('pubDate').get_text(), date_format)

            # During the first run I can get all the news.
            if hasRows == 0 :
                getRTP_Articles(link_wtho_tag,station,function,pub_date)
            else:
                #if the table has tuples get the items that are more recent than the most recent record on the table.
                recentData = Bothasinfo.query.filter(Bothasinfo.fk_station_has_bots_bot_function_id == function, Bothasinfo.fk_station_has_bots_radio_station_id == station).order_by(Bothasinfo.created_at.desc()).first()
                #print pub_date
                #print recentData.created_at
                #print pub_date > recentData.created_at
                if pub_date > recentData.created_at:
                    getRTP_Articles(link_wtho_tag, station, function, pub_date)
                else:
                    #no need to get more news(links) from the rss because the rss links are ordered by data and the most recent ones stay on top
                    print "Every seems up-to-date no need to fetch."
                    break

def getRTP_Articles(link_to_article,station,function,publication_date):
    """
    Get articles and puts them on database.
    :param link_to_article:     (String) The article url
    :param station:             (int)   id of the station
    :param function:            (int)   id of the bot function
    :param publication_date:    (String) Date of the publication
    :return:
    """
    bot_info = ""
    response, content = getpage(link_to_article)
    news_soup = parsepage(content, 'html.parser')
    # get the text from the soup
    #print "Getting the news"
    for new in news_soup.findAll("div", {"itemprop": "articleBody"}):
        bot_info = new.get_text()  # .encode('utf-8')

    if bot_info != "":  # when we don't have anything form the webpage url. (or Weird URLs is received)
        print bot_info.encode('utf-8')
        info = validate_sms(bot_info)
        new_info = Bothasinfo(created_at=publication_date, fk_station_has_bots_bot_function_id=function, fk_station_has_bots_radio_station_id=station, info=info)
        db.session.add(new_info)
        try:
            db.session.commit()
            print "New Saved to Database"
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            print "Error the new could not be saved on database" + str(e)
    else:
        print "No need to update"

def textToDatetime(text,format):
    """
    Conversion of a date to a datetime that can be inserted on database
    :param text:    (String) date that comes in text format
    :param format:  (String) Format of the date that is received on text parameter. More info about formats http://strftime.org/
    :return:
    """
    try:
         date = datetime.strptime(text,format)  # Str to datetime conversion Wed, 10 Aug 2016 18:36:25
    except Exception as e:
        print str(e)
	#send_mail("Error DateTime Conversion",str(e))
    return date
