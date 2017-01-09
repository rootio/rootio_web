import flask
from flask.ext.login import current_user
from . import constants
from .models import User
from ..radio.models import Station, Network

def edit_stations(user=current_user):
    """ A query of stations that the current user can edit """

    if user.is_authenticated():

        if user.role_code == constants.ADMIN:
            return Station.query

        if user.role_code in [constants.NETWORK_ADMIN, constants.NETWORK_USER]:
            return (
                Station.query
                .join(Network)
                .join(User, Network.networkusers)
                .filter(User.id == user.id)
            )

    return Station.query.filter(False)

def can_edit_station(station, user=current_user):
    return station in edit_stations(user)

def deny():
    flask.abort(403)
