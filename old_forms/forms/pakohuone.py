from __future__ import annotations
from enum import Enum

from datetime import datetime
import json
from typing import Any, List, Type, Iterable, Dict

from app.email import make_greet_line, make_signature_line, make_fullname
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_phone_number, make_attribute_privacy_consent
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.forms import RegistrationForm
from app.form_lib.lib import EnumAttribute, BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.form_controller import FormController
from app.form_lib.eventregistrations import EventRegistrations
from app.form_lib.event import Event
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _check_form_submit(self, registrations: EventRegistrations,
                           form: RegistrationForm, event_quotas: Dict[str, Quota], nowtime: int) -> str:
        error_msg = super()._check_form_submit(registrations, form, event_quotas, nowtime)
        if len(error_msg) != 0:
            return error_msg

        # Check escape room availability
        chosen_time = form.time.data
        early_room = form.room1800.data
        later_room = form.room1930.data
        for entry in registrations.get_entries():
            if entry.aika == chosen_time and ((entry.aika == _PAKO_TIME_FIRST and entry.room1800 == early_room) or (
                    entry.time == _PAKO_TIME_SECOND and entry.room1930 == later_room)):
                return 'Valisemasi huone on jo varattu valitsemanasi aikana'

        return error_msg

    def _render_index_view(self, registrations: EventRegistrations,
                           form: RegistrationForm, nowtime, **extra_template_args) -> Any:
        varatut = []
        for entry in registrations.get_entries():
            varatut.append((entry.time, entry.room1800, entry.room1930))
        return super()._render_index_view(registrations, form, nowtime, **{
            'varatut': json.dumps(varatut),
            **extra_template_args})

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        participants = list(model.get_required_participants()) + list(model.get_optional_participants())

        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut OTYn Pakopelipäivä tapahtumaan. Syötit seuraavia tietoja: ",
            "\n'Nimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email(),
            "\nPuhelinnumero: ", recipient.get_phone_number(),
            "\nJoukkuelaisten nimet:\n"] +
            [make_fullname(participant.get_firstname(), participant.get_lastname()) for participant in participants] +
            ["\n\n", make_signature_line()])


_form_name = make_form_name(__file__)

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


def _make_time_attribute(time_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('time', 'Aika *', 'Aika', time_enum, validators=validators)


def _make_room1800_attribute(games_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('room1800', 'Huone (18:00) *', 'Huone (18:00)', games_enum, validators=validators)


def _make_room1930_attribute(games_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('room1930', 'Huone (19:30) *', 'Huone (19:30)', games_enum, validators=validators)


_TimeEnum = choices_to_enum(_form_name, 'time', _get_game_times())
_GameEnum = choices_to_enum(_form_name, 'game', _get_escape_games())

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
]

other_attributes = [
    make_attribute_email(),
    make_attribute_phone_number(),
    _make_time_attribute(_TimeEnum),
    _make_room1800_attribute(_GameEnum),
    _make_room1930_attribute(_GameEnum),
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, participant_attributes, other_attributes, 5, 1, _form_name)

# MEMO: Kept here until validation logic has been designed.
#
# _Form.aika = RadioField('Aika *', choices=get_str_choices(_get_game_times()), validators=[DataRequired()])
# _Form.huone1800 = RadioField('Huone (18:00) *', choices=get_str_choices(_get_escape_games()),
#                              validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_FIRST)])
# _Form.huone1930 = RadioField('Huone (19:30) *', choices=get_str_choices(_get_escape_games()),
#                              validators=[RequiredIfValue(other_field_name='aika', value=_PAKO_TIME_SECOND)])

_event = Event('OTY:n Pakopelipäivä', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59),
               [Quota.default_quota(20, 0)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)
