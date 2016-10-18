#flask-admin views
import pytz

from flask.ext.login import current_user
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.base import AdminIndexView

from ..extensions import db
from widgets import DateDisplayOnlyField

from ..radio.fields import JSONField
from ..radio.models import *
from ..onair.models import *
from ..telephony.models import *

import flask.ext.wtf as wtf
from flask_admin.contrib.sqla import ModelView

class MyModelView(ModelView):
    form_base_class = wtf.Form

def datetime_formatter(view, context, model, name):
    return getattr(model, name).strftime("%Y-%m-%d %H:%M:%S")

class AdminView(MyModelView):
    column_formatters = {'created_at': datetime_formatter, 'updated_at': datetime_formatter}
    form_excluded_columns = ('created_at', 'updated_at','station_cloud','station_transmitter','stations','number_type','person')
    
    def scaffold_form(self):
        form_class = super(AdminView, self).scaffold_form()
        #haven't figured out how to actually get instance 
        # form_class.last_updated = DateDisplayOnlyField('Last Updated',
        #                 default=self._get_field_value(self.model,'updated_at'))
        return form_class

    def is_accessible(self):
        if current_user.is_authenticated():
            return current_user.role_code == 0
        else:
            return False

    def on_model_change(self, form, model, is_created=False):
        #check to ensure all datetime fields have valid timezone
        datetimefields = ['start','end']
        for f in datetimefields:
            if hasattr(model,f):
                field = getattr(model,f)
                if field.tzinfo == None:
                    setattr(model,f,pytz.utc.localize(field))


class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()

class ProgramTypeView(AdminView):
    #force these fields in, because flask-admin model convertor isn't finding them
    def scaffold_form(self):
        form_class = super(ProgramTypeView, self).scaffold_form()
        form_class.definition = JSONField('Definition')
        form_class.phone_functions = JSONField('Phone Functions')
        return form_class

def admin_routes(admin):
    admin.add_view(AdminView(Person, db.session, category='RootIO'))
    admin.add_view(AdminView(Language, db.session, category='RootIO'))
    admin.add_view(AdminView(Network, db.session, category='RootIO'))
    admin.add_view(AdminView(Location, db.session, category='RootIO'))

    admin.add_view(AdminView(PhoneNumber, db.session, category='Telephony')) #, name="PhoneNumber"))
    admin.add_view(AdminView(Message, db.session, category='Telephony'))
    admin.add_view(AdminView(Call, db.session, category='Telephony'))
    admin.add_view(AdminView(Gateway, db.session, category='Telephony'))

    admin.add_view(AdminView(Station, db.session, category='Radio'))
    admin.add_view(AdminView(Program, db.session, category='Radio'))
    admin.add_view(ProgramTypeView(ProgramType, db.session, category='Radio', name="ProgramType"))
    admin.add_view(AdminView(ScheduledProgram, db.session, category='Radio', name="ScheduledProgram"))
    admin.add_view(AdminView(ScheduledBlock, db.session, category='Radio', name="ScheduledBlock"))
    admin.add_view(AdminView(Episode, db.session, category='Radio'))
    admin.add_view(AdminView(OnAirProgram, db.session, category='Radio', name="OnAirProgram"))
    admin.add_view(AdminView(StationAnalytic, db.session, category='Radio'))

