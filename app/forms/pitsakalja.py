from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from app.email import send_email
from typing import Any, List, Iterable, Tuple
from .forms_util.event import Event
from .forms_util.forms import RequiredIf
from .forms_util.form_controller import FormController


_DRINK_ALCOHOLIC = 'Alkoholillinen'
_DRINK_NON_ALCOHOLIC = 'Alkoholiton'

_DRINK_ALCOHOLIC_MILD_BEER = 'Olut'
_DRINK_ALCOHOLIC_MILD_CIDER = 'Siideri'

_PIZZA_MEAT = 'Liha'
_PIZZA_CHICKEN = 'Kana'
_PIZZA_VEGETARIAN = 'Vege'


def _get_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_alcoholic_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC_MILD_BEER,
        _DRINK_ALCOHOLIC_MILD_CIDER
    ]


def _get_pizzas() -> List[str]:
    return [
        _PIZZA_MEAT,
        _PIZZA_CHICKEN,
        _PIZZA_VEGETARIAN
    ]


def _get_choices(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    alkoholi = RadioField('Alkoholillinen/Alkoholiton *', choices=_get_choices(_get_drinks()), validators=[DataRequired()])
    mieto = SelectField('Mieto juoma *', choices=_get_choices(_get_alcoholic_drinks()), validators=[RequiredIf(other_field_name='alkoholi', value="Alkoholillinen")])
    pitsa = SelectField('Pitsa *', choices=_get_choices(_get_pizzas()), validators=[DataRequired()])
    allergiat = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])
    consent0 = BooleanField('Hyväksyn nimeni julkaisemisen tällä sivulla')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = 'pitsakalja'
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    alkoholi = db.Column(db.String(32))
    mieto = db.Column(db.String(32))
    pitsa = db.Column(db.String(32))
    allergiat = db.Column(db.String(256))
    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())



class PitsaKaljaController(FormController):

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
            msg = _make_email(str(form.etunimi.data), str(form.sukunimi.data), count >= event.get_participant_limit())
            flash(_make_success_msg(reserve))
            send_email(msg, 'OTiT Pitsakaljasitsit ilmoittautuminen', str(form.email.data))

            return redirect(url_for('pitsakaljasitsit'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'pitsakalja/data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Pitsakalja', datetime(2021, 10, 26, 12, 00, 00), datetime(2021, 11, 9, 23, 59, 59), 60, 30)


def _form_to_model (form, nowtime):
    return _Model(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        email=form.email.data,
        alkoholi=form.alkoholi.data,
        mieto=form.mieto.data,
        pitsa=form.pitsa.data,
        allergiat=form.allergiat.data,
        consent0=form.consent0.data,
        consent1=form.consent1.data,
        datetime=nowtime
    )


def _render_form(entries, count, event, nowtime, form):
    return render_template('index.html',
                           title='pitsakaljasitsit ilmoittautuminen',
                           entrys=entries,
                           totalcount=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="pitsakaljasitsit")


def _make_email(firstname: str, lastname: str, reserve: bool):
    if reserve:
        return ' '.join([
            "\"Hei", firstname, " ", lastname,
            "\n\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Olet varasijalla. ",
            "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
            "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
            "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\"",
        ])
    else:
        return ' '.join([
            "\"Hei", firstname, " ", lastname,
            "\n\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Tässä vielä maksuohjeet: ",
            "\n\n", "Hinta alkoholillisen juoman kanssa on 20€ ja alkoholittoman juoman ",
            "kanssa 17€. Maksu tapahtuu tilisiirrolla Oulun Tietoteekkarit ry:n tilille ",
            "FI03 4744 3020 0116 87. Kirjoita viestikenttään nimesi, ",
            "Pitsakalja-sitsit sekä alkoholiton tai alkoholillinen valintasi mukaan.",
            "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
            "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""])


def _make_success_msg(reserve: bool):
    if reserve:
        return 'Ilmoittautuminen onnistui, olet varasijalla'
    else:
        return 'Ilmoittautuminen onnistui'