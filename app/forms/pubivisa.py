from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from typing import Any
from .forms_util.forms import get_guild_choices
from .forms_util.guilds import *
from .forms_util.event import Event
from .forms_util.form_controller import FormController


class _Form(FlaskForm):
    teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])

    etunimi0 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi0 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email0 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta0 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone1 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email1 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta1 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone2 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email2 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta2 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

    etunimi3 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi3 = StringField('Sukunimi', validators=[length(max=50)])
    phone3 = StringField('Puhelinnumero', validators=[length(max=20)])
    email3 = StringField('Sähköposti', validators=[length(max=100)])
    kilta3 = SelectField('Kilta', choices=get_guild_choices(get_all_guilds()))

    consent0 = BooleanField('Sallin joukkueen nimen julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = 'pubivisa'
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(128))

    etunimi0 = db.Column(db.String(64))
    sukunimi0 = db.Column(db.String(64))
    phone0 = db.Column(db.String(32))
    email0 = db.Column(db.String(128))
    kilta0 = db.Column(db.String(16))

    etunimi1 = db.Column(db.String(64))
    sukunimi1 = db.Column(db.String(64))
    phone1 = db.Column(db.String(32))
    email1 = db.Column(db.String(128))
    kilta1 = db.Column(db.String(16))

    etunimi2 = db.Column(db.String(64))
    sukunimi2 = db.Column(db.String(64))
    phone2 = db.Column(db.String(32))
    email2 = db.Column(db.String(128))
    kilta2 = db.Column(db.String(16))

    etunimi3 = db.Column(db.String(64))
    sukunimi3 = db.Column(db.String(64))
    phone3 = db.Column(db.String(32))
    email3 = db.Column(db.String(128))
    kilta3 = db.Column(db.String(16))

    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    consent2 = db.Column(db.Boolean())

    datetime = db.Column(db.DateTime())

    personcount = db.Column(db.Integer())


class PubiVisaController(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()
        totalcount = 0
        for entry in entries:
            totalcount += entry.personcount

        return _render_form(entries, totalcount, event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        totalcount = 0
        for entry in entries:
            totalcount += entry.personcount

        group_size = 0
        group_size += int(form.etunimi0.data and form.sukunimi0.data)
        group_size += int(form.etunimi1.data and form.sukunimi1.data)
        group_size += int(form.etunimi2.data and form.sukunimi2.data)
        group_size += int(form.etunimi3.data and form.sukunimi3.data)
        totalcount += group_size

        if nowtime > event.get_end_time():
            flash('Ilmoittautuminen on päättynyt')
            return _render_form(entries, totalcount, event, nowtime, form)

        if totalcount >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            totalcount -= group_size
            return _render_form(entries, totalcount, event, nowtime, form)

        teamname = form.teamname.data
        for entry in entries:
            if entry.teamname == teamname:
                flash('Olet jo ilmoittautunut')

                return _render_form(entries, totalcount, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(_form_to_model(form, group_size, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            return redirect(url_for('route_get_pubivisa'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, totalcount, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'pubivisa/data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Pubivisa', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 10, 23, 59, 59), 50, 0)


def _render_form(entrys, count, event, nowtime, form):
    return render_template('pubivisa/index.html',
                           title='pubivisa ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="pubivisa")


def _form_to_model(form, count, nowtime):
    return _Model(
        teamname=form.teamname.data,
        etunimi0=form.etunimi0.data,
        sukunimi0=form.sukunimi0.data,
        phone0=form.phone0.data,
        email0=form.email0.data,
        kilta0=form.kilta0.data,
        etunimi1=form.etunimi1.data,
        sukunimi1=form.sukunimi1.data,
        phone1=form.phone1.data,
        email1=form.email1.data,
        kilta1=form.kilta1.data,
        etunimi2=form.etunimi2.data,
        sukunimi2=form.sukunimi2.data,
        phone2=form.phone2.data,
        email2=form.email2.data,
        kilta2=form.kilta2.data,
        etunimi3=form.etunimi3.data,
        sukunimi3=form.sukunimi3.data,
        phone3=form.phone3.data,
        email3=form.email3.data,
        kilta3=form.kilta3.data,
        consent0=form.consent0.data,
        consent1=form.consent1.data,
        consent2=form.consent2.data,
        personcount=count,
        datetime=nowtime
    )
