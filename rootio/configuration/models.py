# -*- coding: utf-8 -*-
from coaster.sqlalchemy import BaseMixin
from sqlalchemy.sql import func

from ..extensions import db


class VoicePrompt(BaseMixin, db.Model):
    """Configurable voice prompts for stations"""
    __tablename__ = u"configuration_voiceprompt"

    station_id = db.Column(db.ForeignKey('radio_station.id'))

    on_air = db.Column(db.String(200))
    on_air_txt = db.Column(db.Text())
    call_end = db.Column(db.String(200))
    call_end_txt = db.Column(db.Text())
    call_end_part2 = db.Column(db.String(200))
    call_end_part2_txt = db.Column(db.Text())
    incoming_call = db.Column(db.String(200))
    incoming_call_txt = db.Column(db.Text())
    host_welcome = db.Column(db.String(200))
    host_welcome_txt = db.Column(db.Text())
    host_wait = db.Column(db.String(200))
    host_wait_txt = db.Column(db.Text())
    wake_mode_activation = db.Column(db.String(200))
    wake_mode_activation_txt = db.Column(db.Text())
    incoming_reject_activation = db.Column(db.String(200))
    incoming_reject_activation_txt = db.Column(db.Text())
    incoming_answer_activation = db.Column(db.String(200))
    incoming_answer_activation_txt = db.Column(db.Text())
    incoming_queue_activation = db.Column(db.String(200))
    incoming_queue_activation_txt = db.Column(db.Text())
    take_break = db.Column(db.String(200))
    take_break_txt = db.Column(db.Text())
    input_number = db.Column(db.String(200))
    input_number_txt = db.Column(db.Text())
    calling_number = db.Column(db.String(200))
    calling_number_txt = db.Column(db.Text())
    call_queued = db.Column(db.String(200))
    call_queued_txt = db.Column(db.Text())
    call_queued_part2 = db.Column(db.String(200))
    call_queued_part2_txt = db.Column(db.Text())
    call_failed = db.Column(db.String(200))
    call_failed_txt = db.Column(db.Text())
    call_failed_part2 = db.Column(db.String(200))
    call_failed_part2_txt = db.Column(db.Text())
    call_back_hangup = db.Column(db.String(200))
    call_back_hangup_txt = db.Column(db.Text())
    call_back_wait = db.Column(db.String(200))
    call_back_wait_txt = db.Column(db.Text())

    use_tts = db.Column(db.Boolean(), default=False)
    prefetch_tts = db.Column(db.Boolean(), default=True)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    station = db.relationship(u'Station', backref=db.backref('voice_prompt'))

    deleted = db.Column(db.Boolean)
