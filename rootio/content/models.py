'''from ..utils import STRING_LEN, GENDER_TYPE, id_generator, object_list_to_named_dict
from ..extensions import db



class Track(BaseMixin, db.Model):
    "A track record"
    __tablename__ = u'radio_location'

    name = db.Column(db.String(STRING_LEN))
    description = db.Column(db.Text)
    type = db.Column(db.String(STRING_LEN))
 

    def __unicode__(self):
        return self.name'''