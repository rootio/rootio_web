import flask
from flask.ext.login import current_user
from . import constants
from .models import User
from ..radio.models import Station, Network

def is_logged_in(user=current_user):
    return user.is_authenticated()

def edit_networks(user=current_user):
    """ A query of networks that the current user can edit """

    if user.is_authenticated():

        if user.role_code == constants.ADMIN:
            return Network.query

        if user.role_code == constants.NETWORK_ADMIN:
            return (
                Network.query
                .join(User, Network.networkusers)
                .filter(User.id == user.id)
            )

    return Network.query.filter(False)

def can_edit_network(network, user=current_user):
    return network in edit_networks(user)

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

def can_admin(user=current_user):
    if user.is_authenticated():
        if user.role_code == constants.ADMIN:
            return True

    return False

def deny():
    flask.abort(403)
