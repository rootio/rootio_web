#flask-admin views
from flask.ext.login import current_user
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.base import AdminIndexView
import flask_wtf

from ..extensions import db

from ..radio.models import *
from ..onair.models import *
from ..telephony.models import *

class AdminView(ModelView):
    form_base_class = flask_wtf.Form

    def is_accessible(self):
        if current_user.is_authenticated():
            return current_user.role_code == 0
        else:
            return False

class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()

def admin_routes(admin):
    admin.add_view(AdminView(Person, db.session, category='RootIO'))
    admin.add_view(AdminView(Language, db.session, category='RootIO'))
    admin.add_view(AdminView(Network, db.session, category='RootIO'))
    admin.add_view(AdminView(Location, db.session, category='RootIO'))
    admin.add_view(AdminView(ProgramType, db.session, category='RootIO', name="ProgramType"))

    admin.add_view(AdminView(PhoneNumber, db.session, category='Telephony', name="PhoneNumber"))
    admin.add_view(AdminView(Message, db.session, category='Telephony'))
    admin.add_view(AdminView(Call, db.session, category='Telephony'))

    admin.add_view(AdminView(Station, db.session, category='Radio'))
    admin.add_view(AdminView(Program, db.session, category='Radio'))
    admin.add_view(AdminView(ScheduledProgram, db.session, category='Radio', name="ScheduledProgram"))
    admin.add_view(AdminView(ScheduledBlock, db.session, category='Radio', name="ScheduledBlock"))
    admin.add_view(AdminView(Episode, db.session, category='Radio'))
    admin.add_view(AdminView(OnAirProgram, db.session, category='Radio', name="OnAirProgram"))

