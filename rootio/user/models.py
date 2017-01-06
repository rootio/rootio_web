# -*- coding: utf-8 -*-

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from ..extensions import db
from ..utils import get_current_time, GENDER_TYPE, STRING_LEN
from .constants import NETWORK_USER, USER_ROLE, ADMIN, INACTIVE, USER_STATUS

class UserDetail(db.Model):
    __tablename__ = 'user_details'

    id = Column(db.Integer, primary_key=True)

    age = Column(db.Integer)
    phone = Column(db.String(STRING_LEN))
    url = Column(db.String(STRING_LEN))
    location = Column(db.String(STRING_LEN))
    bio = Column(db.String(STRING_LEN))

    gender_code = db.Column(db.Integer)
    user = db.relationship("User", enable_typechecks=False, uselist=False, backref="user_detail")


    @property
    def gender(self):
        return GENDER_TYPE.get(self.gender_code)

    created_time = Column(db.DateTime, default=get_current_time)


class RootioUser(db.Model):
    __tablename__ = 'user_user'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(STRING_LEN))
    email = Column(db.String(STRING_LEN), nullable=False, unique=True)
    openid = Column(db.String(STRING_LEN), unique=True)
    activation_key = Column(db.String(STRING_LEN))
    created_time = Column(db.DateTime, default=get_current_time)
    last_accessed = Column(db.DateTime)
    networks = db.relationship(u'Network', secondary=u'radio_networkusers', backref=db.backref('networkusers'))
    avatar = Column(db.String(STRING_LEN))
    _password = Column('password', db.String(STRING_LEN*3), nullable=False)

    role_code = Column(db.SmallInteger, default=NETWORK_USER)
    status_code = Column(db.SmallInteger, default=INACTIVE)
    user_detail_id = Column(db.Integer, db.ForeignKey("user_details.id"))



class User(RootioUser, UserMixin):

    def __unicode__(self):
        return self.name

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)
    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password.encode('latin-1'), password)


    @property
    def role(self):
        return USER_ROLE[self.role_code]
    
    def is_admin(self):
        return self.role_code == ADMIN

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    # ================================================================
    # Class methods

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(db.or_(User.name == login, User.email == login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0
