from wtforms import RadioField
from wtforms.validators import DataRequired, InputRequired
from datetime import datetime
import json
from typing import Any, List

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.forms import RequiredIfValue, get_str_choices, BasicForm, ParticipantFormBuilder, \
    make_field_firstname, make_field_lastname, make_field_phone_number, FormBuilder, make_field_required_participants,\
    make_field_privacy_consent, make_field_optional_participants, RequiredIf
from app.form_lib.lib import ATTRIBUTE_NAME_FIRSTNAME
from app.form_lib.form_controller import FormController, DataTableInfo, Event, EventRegistrations, Quota
from app.form_lib.models import BasicModel, basic_model_csv_map, phone_number_csv_map

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


_Participant = ParticipantFormBuilder().add_fields([
    make_field_firstname([InputRequired()]),
    make_field_lastname([InputRequired()])
]).build()

_OptionalParticipant = ParticipantFormBuilder().add_fields([
    make_field_firstname(),
    make_field_lastname([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)])
]).build()

_Form = FormBuilder().add_fields([
    make_field_phone_number([InputRequired()]),
    make_field_required_participants(_Participant, 5),
    make_field_optional_participants(_OptionalParticipant, 1),
    make_field_privacy_consent()
]).build()

_Form.aika = RadioField('Aika *', choices=get_str_choices(_get_game_times()), validators=[DataRequired()])
_Form.huone1800 = RadioField('Huone (18:00) *', choices=get_str_choices(_get_escape_games()),
                             validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_FIRST)])
_Form.huone1930 = RadioField('Huone (19:30) *', choices=get_str_choices(_get_escape_games()),
                             validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_SECOND)])


class _Model(BasicModel): #, PhoneNumberColumn):
    __tablename__ = _form_name
    aika = db.Column(db.String(16))
    huone1800 = db.Column(db.String(64))
    huone1930 = db.Column(db.String(64))

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

    def get_participant_count(self) -> int:
        return int(bool(self.firstname and self.lastname)) \
             + int(bool(self.etunimi1 and self.sukunimi1)) \
             + int(bool(self.etunimi2 and self.sukunimi2)) \
             + int(bool(self.etunimi3 and self.sukunimi3)) \
             + int(bool(self.etunimi4 and self.sukunimi4)) \
             + int(bool(self.etunimi5 and self.sukunimi5))

    def get_quota_counts(self) -> List[Quota]:
        return [
            Quota.default_quota(int(bool(self.firstname and self.lastname)), 0),
            Quota.default_quota(int(bool(self.etunimi1 and self.sukunimi1)), 0),
            Quota.default_quota(int(bool(self.etunimi2 and self.sukunimi2)), 0),
            Quota.default_quota(int(bool(self.etunimi3 and self.sukunimi3)), 0),
            Quota.default_quota(int(bool(self.etunimi4 and self.sukunimi4)), 0),
            Quota.default_quota(int(bool(self.etunimi5 and self.sukunimi5)), 0)
        ]


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
_event = Event('OTY:n Pakopelipäivä', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59),
               [Quota.default_quota(20, 0)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
