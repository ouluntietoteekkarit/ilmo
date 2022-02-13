from flask_wtf import FlaskForm
from flask import url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import json
from typing import Any

from app import db
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.forms import RequiredIfValue
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

"""Singleton instance containing this form module's information."""
_form_module = None
_form_name = file_path_to_form_name(__file__)


def get_module_info() -> ModuleInfo:
    """
    Returns this form's module information.
    """
    global _form_module
    if _form_module is None:
        _form_module = ModuleInfo(_Controller, True, _form_name)
    return _form_module


# P U B L I C   M O D U L E   I N T E R F A C E   E N D


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


class _Form(FlaskForm):
    aika = RadioField('Aika *', choices=_get_time_choices(), validators=[DataRequired()])
    huone1800 = RadioField('Huone (18:00) *', choices=_get_game_choices(),
                           validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_FIRST)])
    huone1930 = RadioField('Huone (19:30) *', choices=_get_game_choices(),
                           validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_SECOND)])

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


class _Model(db.Model):
    __tablename__ = _form_name
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

    def get_firstname(self) -> str:
        return self.etunimi0

    def get_lastname(self) -> str:
        return self.sukunimi0

    def get_email(self) -> str:
        return self.email0

    def get_show_name_consent(self) -> bool:
        return False


class _Controller(FormController):

    def __init__(self):
        event = Event('Pakopelipäivä ilmoittautuminen', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59), 20, 0)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        count = len(entries)

        error_msg = self._check_form_submit(event, form, entries, nowtime, count)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(entries, event, nowtime, form)

        chosen_time = form.aika.data
        early_room = form.huone1800.data
        later_room = form.huone1930.data
        for entry in entries:
            if entry.aika == chosen_time and ((entry.aika == _PAKO_TIME_FIRST and entry.huone1800 == early_room) or (
                    entry.aika == _PAKO_TIME_SECOND and entry.huone1930 == later_room)):
                flash('Valisemasi huone on jo varattu valitsemanasi aikana')
                return self._render_index_view(entries, count, event, nowtime, form)

        db.session.add(self._form_to_model(form, nowtime))
        db.session.commit()

        flash('Ilmoittautuminen onnistui')
        return self._render_index_view(entries, count, event, nowtime, form)

    def _render_index_view(self, entries, event: Event, nowtime, form: _Form, **extra_template_args) -> Any:
        varatut = []
        for entry in entries:
            varatut.append((entry.aika, entry.huone1800, entry.huone1930))
        return super()._render_index_view(entries, event, nowtime, form, **{
            'varatut': json.dumps(varatut),
            **extra_template_args})

    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi0.data
        lastname = form.sukunimi0.data
        email = form.email0.data
        for entry in entries:
            if (entry.etunimi0 == firstname and entry.sukunimi0 == lastname) or entry.email0 == email:
                return True
        return False

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email0.data)

    def _get_email_msg(self, form: _Form, reserve: bool) -> str:
        return ' '.join(["\"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
                         "\n\nOlet ilmoittautunut OTYn Pakopelipäivä tapahtumaan. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", str(form.etunimi0.data), str(form.sukunimi0.data),
                         "\nSähköposti: ", str(form.email0.data),
                         "\nPuhelinnumero: ", str(form.phone0.data),
                         "\nMuiden joukkuelaisten nimet: ", str(form.etunimi1.data), str(form.sukunimi1.data),
                         str(form.etunimi2.data), str(form.sukunimi2.data),
                         str(form.etunimi3.data), str(form.sukunimi3.data),
                         str(form.etunimi4.data), str(form.sukunimi4.data),
                         str(form.etunimi5.data), str(form.sukunimi5.data),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])

    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        return _Model(
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


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('aika', 'aika'),
        ('huone1800', 'huone1800'),
        ('huone1930', 'huone1930'),
        ('etunimi0', 'etunimi0'),
        ('sukunimi0', 'sukunimi0'),
        ('phone0', 'phone0'),
        ('email0', 'email0'),
        ('etunimi1', 'etunimi1'),
        ('sukunimi1', 'sukunimi1'),
        ('etunimi2', 'etunimi2'),
        ('sukunimi2', 'sukunimi2'),
        ('etunimi3', 'etunimi3'),
        ('sukunimi3', 'sukunimi3'),
        ('etunimi4', 'etunimi4'),
        ('sukunimi4', 'sukunimi4'),
        ('etunimi5', 'etunimi5'),
        ('sukunimi5', 'sukunimi5'),
        ('consent0', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
