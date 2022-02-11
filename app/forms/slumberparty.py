from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from typing import Any
from .forms_util.guilds import *
from .forms_util.event import Event
from .forms_util.form_controller import FormController


def _get_guild_choices():
    choices = []
    for guild in get_all_guilds():
        choices.append((guild.get_name(), guild.get_name()))
    return choices


class SlumberpartyForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta = SelectField('Kilta *', choices=_get_guild_choices())
    consent0 = BooleanField('Sallin nimeni julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class SlumberpartyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    email = db.Column(db.String(128))
    kilta = db.Column(db.String(16))
    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    consent2 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


class SlumberPartyController(FormController):

    def get_request_handler(self, request) -> Any:
        form = SlumberpartyForm()
        event = self._get_event()
        entries = SlumberpartyModel.query.all()

        return _render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        form = SlumberpartyForm()
        event = self._get_event()
        nowtime = datetime.now()
        entries = SlumberpartyModel.query.all()
        count = len(entries)

        if count >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            return _render_form(entries, count, event, nowtime, form)

        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                flash('Olet jo ilmoittautunut')
                return _render_form(entries, count, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(_form_to_model(form, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            return redirect(url_for('route_get_slumberparty'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(SlumberpartyModel, 'slumberparty/slumberparty_data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(SlumberpartyModel.__tablename__)

    def _get_event(self) -> Event:
        return Event('Slumberparty', datetime(2020, 10, 21, 12, 00, 00), datetime(2020, 10, 27, 23, 59, 59), 50)


def _render_form(entrys, count, event, nowtime, form):
    return render_template('slumberparty/slumberparty.html',
                           title='slumberparty ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="slumberparty")


def _form_to_model(form, nowtime):
    return SlumberpartyModel(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        phone=form.phone.data,
        email=form.email.data,
        kilta=form.kilta.data,
        consent0=form.consent0.data,
        consent1=form.consent1.data,
        consent2=form.consent2.data,
        datetime=nowtime
    )
