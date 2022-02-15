from wtforms import StringField, RadioField
from wtforms.validators import DataRequired, length
from datetime import datetime
import json
from typing import Any

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import RequiredIfValue, PhoneNumberField, get_str_choices, BasicForm
from .forms_util.form_controller import FormController, DataTableInfo, Event, EventRegistrations
from .forms_util.models import BasicModel, PhoneNumberColumn, basic_model_csv_map, phone_number_csv_map

_form_name = file_path_to_form_name(__file__)

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


def _get_game_times():
    return [
        _PAKO_TIME_FIRST,
        _PAKO_TIME_SECOND
    ]


@PhoneNumberField()
class _Form(BasicForm):
    aika = RadioField('Aika *', choices=get_str_choices(_get_game_times()), validators=[DataRequired()])
    huone1800 = RadioField('Huone (18:00) *', choices=get_str_choices(_get_escape_games()),
                           validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_FIRST)])
    huone1930 = RadioField('Huone (19:30) *', choices=get_str_choices(_get_escape_games()),
                           validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_SECOND)])

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


class _Model(BasicModel, PhoneNumberColumn):
    __tablename__ = _form_name
    aika = db.Column(db.String(16))
    huone1800 = db.Column(db.String(128))
    huone1930 = db.Column(db.String(128))

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


class _Controller(FormController):

    def _check_form_submit(self, registrations: EventRegistrations, form: BasicForm, nowtime) -> str:
        error_msg = super()._check_form_submit(registrations, form, nowtime)
        if len(error_msg) != 0:
            return error_msg

        # Check escape room availability
        chosen_time = form.aika.data
        early_room = form.huone1800.data
        later_room = form.huone1930.data
        for entry in registrations.get_entries():
            if entry.aika == chosen_time and ((entry.aika == _PAKO_TIME_FIRST and entry.huone1800 == early_room) or (
                    entry.aika == _PAKO_TIME_SECOND and entry.huone1930 == later_room)):
                return 'Valisemasi huone on jo varattu valitsemanasi aikana'

        return error_msg

    def _render_index_view(self, registrations: EventRegistrations, form: _Form, nowtime, **extra_template_args) -> Any:
        varatut = []
        for entry in registrations.get_entries():
            varatut.append((entry.aika, entry.huone1800, entry.huone1930))
        return super()._render_index_view(registrations, form, nowtime, **{
            'varatut': json.dumps(varatut),
            **extra_template_args})

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut OTYn Pakopelipäivä tapahtumaan. Syötit seuraavia tietoja: ",
            "\n'Nimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email_address(),
            "\nPuhelinnumero: ", model.get_phone_number(),
            "\nJoukkuelaisten nimet: ",
            "\n", model.firstname, " ", model.lastname,
            "\n", model.etunimi1, " ", model.sukunimi1,
            "\n", model.etunimi2, " ", model.sukunimi2,
            "\n", model.etunimi3, " ", model.sukunimi3,
            "\n", model.etunimi4, " ", model.sukunimi4,
            "\n", model.etunimi5, " ", model.sukunimi5,
            "\n\n", make_signature_line()
        ])


# MEMO: (attribute, header_text)
_data_table_info = DataTableInfo([
    ('aika', 'aika'),
    ('huone1800', 'huone1800'),
    ('huone1930', 'huone1930')] +
    basic_model_csv_map() +
    phone_number_csv_map() + [
    ('etunimi1', 'etunimi1'),
    ('sukunimi1', 'sukunimi1'),
    ('etunimi2', 'etunimi2'),
    ('sukunimi2', 'sukunimi2'),
    ('etunimi3', 'etunimi3'),
    ('sukunimi3', 'sukunimi3'),
    ('etunimi4', 'etunimi4'),
    ('sukunimi4', 'sukunimi4'),
    ('etunimi5', 'etunimi5'),
    ('sukunimi5', 'sukunimi5')])
_event = Event('Pakopelipäivä ilmoittautuminen', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59),
               20, 0, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
