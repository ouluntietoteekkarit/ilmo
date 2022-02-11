from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from app.email import send_email
from typing import Any, List, Iterable, Tuple
from .forms_util.event import Event
from .forms_util.form_controller import FormController

_PARTICIPANT_FUKSI = 'Fuksi'
_PARTICIPANT_PRO = 'Pro'
_PARTICIPANT_BOARD_MEMBER = 'Hallitus'
_PARTICIPANT_OTHER = 'Muu'

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_participants() -> List[str]:
    return [
        _PARTICIPANT_FUKSI,
        _PARTICIPANT_PRO,
        _PARTICIPANT_BOARD_MEMBER,
        _PARTICIPANT_OTHER
    ]


def _get_choise(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    puh = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    lahtopaikka = SelectField('Lähtöpaikka *', choices=_get_choise(_get_departure_stops()), validators=[DataRequired()])
    kiintio = SelectField('Kiintiö *', choices=_get_choise(_get_participants()), validators=[DataRequired()])
    consent0 = BooleanField('Hyväksyn nimeni julkaisemisen tällä sivulla')
    consent1 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = 'fucu'
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    puh = db.Column(db.String(32))
    lahtopaikka = db.Column(db.String(32))
    kiintio = db.Column(db.String(32))
    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


class FucuController(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()

        return _render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        count = len(entries)
        maxlimit = event.get_participant_limit() + event.get_participant_reserve()

        if count >= maxlimit:
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

            reserve = count >= event.get_participant_limit()
            msg = _make_email(str(form.etunimi.data), str(form.sukunimi.data), str(form.email.data),
                              str(form.puh.data), str(form.lahtopaikka.data), str(form.kiintio.data), reserve)
            flash(_make_success_msg(reserve))
            send_email(msg, 'OTiT Fuksicursio ilmoittautuminen', str(form.email.data))

            return redirect(url_for('route_get_fucu'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'fucu/data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Fucu', datetime(2021, 10, 29, 12, 00, 00), datetime(2021, 11, 4, 21, 00, 00), 100, 20)


def _form_to_model(form, nowtime):
    return _Model(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        email=form.email.data,
        puh=form.puh.data,
        lahtopaikka=form.lahtopaikka.data,
        kiintio=form.kiintio.data,
        consent0=form.consent0.data,
        consent1=form.consent1.data,
        datetime=nowtime
    )


def _render_form(entries, count, event, nowtime, form):
    return render_template('fucu/index.html',
                           title='fucu ilmoittautuminen',
                           entrys=entries,
                           totalcount=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="fucu")


def _make_email(firstname: str, lastname: str, email: str, phone_number: str,
                departure_location: str, quota: str, reserve: bool):
    if reserve:
        return ' '.join([
            "\"Hei", firstname, " ", lastname,
            "\n\nOlet ilmoittautunut OTiTin Fuksicursiolle. Olet varasijalla. ",
            "Jos fuculle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
            "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""
        ])
    else:
        return ' '.join([
            "\"Hei", firstname, " ", lastname,
            "\n\nOlet ilmoittautunut OTiTin Fuksicursiolle. Tässä vielä syöttämäsi tiedot: ",
            "\n\nNimi: ", firstname, lastname,
            "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
            "\nLähtöpaikka: ", departure_location, "\nKiintiö: ", quota,
            "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""
        ])


def _make_success_msg(reserve: bool):
    if reserve:
        return 'Ilmoittautuminen onnistui, olet varasijalla'
    else:
        return 'Ilmoittautuminen onnistui'
