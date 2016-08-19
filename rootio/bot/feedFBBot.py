# -*- coding: utf-8 -*-

from datetime import datetime

from rootio.radio.models import Bothasinfo

from rootio.extensions import db

import requests

from facebook import GraphAPI

# Facebook app details
FB_APP_ID = '637462246416071'
FB_APP_SECRET = '3d0eff71edaacc9eea101484fb325b9a'

# Gets the most recent posts from a Facebook page since the last run
# page (string) -> id of the FB page
# staion (int) -> id of the station
# function (int) -> id of the function
def getPosts(page,station,function):
    # Gets an access token to allow us to fetch information from FB pages
    r = requests.get('https://graph.facebook.com/oauth/access_token?client_id='+FB_APP_ID+'&client_secret='+FB_APP_SECRET+'&grant_type=client_credenti
als')
    access_token = r.text[13:]
    graph = GraphAPI(access_token)
    profile = graph.get_object(user)
    # Gets the last info that was introduced into the database
    last_bot_info = Bothasinfo.query.filter(Bothasinfo.fk_station_has_bots_radio_station_id == station, Bothasinfo.fk_station_has_bots_bot_function_id == function).order_by(Bothasinfo.created_at.desc()).first()
    if last_bot_info == None:
        last_info_date = datetime.now()
    else:
        last_info_date = last_bot_info.created_at
    posts = graph.get_connections(profile['id'], 'posts')
    for post in posts['data']:
        # This condition grants that we only get info from posts
        if 'message' in post:
            if datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S+%f") > last_info_date:
	        info = post['message'].encode('utf8')
                new_info = Bothasinfo(created_at = post['created_time'], fk_station_has_bots_radio_station_id = 15 , fk_station_has_bots_bot_function_id = 1, info = info)
                db.session.add(new_info)
                db.session.commit()

