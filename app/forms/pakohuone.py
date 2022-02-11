from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import json
from app import db
from typing import Any
from .forms_util.forms import RequiredIfValue
from .forms_util.event import Event
from .forms_util.form_controller import FormController


_PAKO_TIME_FIRST = '18:00'
_PAKO_TIME_SECOND = '19:30'


def _get_escape_games():
    return [
       'Pommi (Uusikatu)',
       'Kuolleen miehen saari (Uusikatu)',
       'Temppelin kirous (Uusikatu)',
       'Velhon perintö (Uusikatu)',
       'Murhamysteeri (Kajaaninkatu)',
       'Vankilapako (Kajaaninkatu)',
       'Professorin arvoitus (Kajaaninkatu)',
       'The SAW (Kirkkokatu)',
       'Alcatraz (Kirkkokatu)',
       'Matka maailman ympäri (Kirkkokatu)',
    ]


def _get_game_choices():
    choices = []
    for game in _get_escape_games():
        choices.append((game, game))
    return choices


def _get_game_times():
    return [
        _PAKO_TIME_FIRST,
        _PAKO_TIME_SECOND
    ]


def _get_time_choices():
    choices = []
    for time in _get_game_times():
        choices.append((time, time))
    return choices


class PakohuoneForm(FlaskForm):
    aika = RadioField('Aika *', choices=_get_time_choices(), validators=[DataRequired()])
    huone1800 = RadioField('Huone (18:00) *', choices=_get_game_choices(), validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_FIRST)])
    huone1930 = RadioField('Huone (19:30) *', choices=_get_game_choices(), validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_SECOND)])

    etunimi0 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi0 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email0 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi3 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi3 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi4 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi4 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi5 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi5 = StringField('Sukunimi', validators=[length(max=50)])

    consent0 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class PakohuoneModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    aika = db.Column(db.String(16))
    huone1800 = db.Column(db.String(128))
    huone1930 = db.Column(db.String(128))

    etunimi0 = db.Column(db.String(64))
    sukunimi0 = db.Column(db.String(64))
    phone0 = db.Column(db.String(32))
    email0 = db.Column(db.String(128))

    etunimi1 = db.Column(db.String(64))
    sukunimi1 = db.Column(db.String(64))

    etunimi2 = db.Column(db.String(64))
    sukunimi2 = db.Column(db.String(64))

    etunimi3 = db.Column(db.String(64))
    sukunimi3 = db.Column(db.String(64))

    etunimi4 = db.Column(db.String(64))
    sukunimi4 = db.Column(db.String(64))

    etunimi5 = db.Column(db.String(64))
    sukunimi5 = db.Column(db.String(64))

    consent0 = db.Column(db.Boolean())

    datetime = db.Column(db.DateTime())


class PakoHuoneController(FormController):

    def get_request_handler(self, request) -> Any:
        form = PakohuoneForm()
        event = self._get_event()
        entries = PakohuoneModel.query.all()

        varatut = []
        for entry in entries:
            varatut.append((entry.aika, entry.huone1800, entry.huone1930))

        return _render_form(entries, len(entries), event, datetime.now(), form, varatut)

    def post_request_handler(self, request) -> Any:
        form = PakohuoneForm()
        event = self._get_event()
        nowtime = datetime.now()
        entries = PakohuoneModel.query.all()
        count = len(entries)

        varatut = []
        for entry in entries:
            varatut.append((entry.aika, entry.huone1800, entry.huone1930))

        if count >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            return _render_form(entries, count, event, nowtime, form, varatut)

        firstname = form.etunimi0.data
        lastname = form.sukunimi0.data
        email = form.email0.data
        for entry in entries:
            if (entry.etunimi0 == firstname and entry.sukunimi0 == lastname) or entry.email0 == email:
                flash('Olet jo ilmoittautunut')
                return _render_form(entries, count, event, nowtime, form, varatut)

        chosen_time = form.aika.data
        early_room = form.huone1800.data
        later_room = form.huone1930.data
        for entry in entries:
            if entry.aika == chosen_time and ((entry.aika == _PAKO_TIME_FIRST and entry.huone1800 == early_room) or (entry.aika == _PAKO_TIME_SECOND and entry.huone1930 == later_room)):
                flash('Valisemasi huone on jo varattu valitsemanasi aikana')
                return _render_form(entries, count, event, nowtime, form, varatut)

        if form.validate_on_submit():
            db.session.add(_form_to_model(form, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            return redirect(url_for('route_get_pakohuone'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form, varatut)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(PakohuoneModel, 'pakohuone/pakohuone_data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(PakohuoneModel.__tablename__)

    def _get_event(self) -> Event:
        return Event('Pakohuone', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59), 20)


def _render_form(entrys, count, event, nowtime, form, varatut):
    return render_template('pakohuone/pakohuone.html',
                           title='pakohuone ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           varatut=json.dumps(varatut),
                           page="pakohuone")


def _form_to_model(form, nowtime):
    return PakohuoneModel(
        aika=form.aika.data,
        huone1800=form.huone1800.data,
        huone1930=form.huone1930.data,
        etunimi0=form.etunimi0.data,
        sukunimi0=form.sukunimi0.data,
        phone0=form.phone0.data,
        email0=form.email0.data,
        etunimi1=form.etunimi1.data,
        sukunimi1=form.sukunimi1.data,
        etunimi2=form.etunimi2.data,
        sukunimi2=form.sukunimi2.data,
        etunimi3=form.etunimi3.data,
        sukunimi3=form.sukunimi3.data,
        etunimi4=form.etunimi4.data,
        sukunimi4=form.sukunimi4.data,
        etunimi5=form.etunimi5.data,
        sukunimi5=form.sukunimi5.data,
        consent0=form.consent0.data,
        datetime=nowtime
    )
