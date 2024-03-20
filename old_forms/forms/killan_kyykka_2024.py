from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Iterable, Type

from wtforms.validators import InputRequired, Email, Length

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_lastname, make_attribute_firstname, make_attribute_email, \
    make_attribute_quota, make_attribute_privacy_consent, make_attribute_name_consent, make_attribute_allergies
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.guilds import GUILD_OTIT, GUILD_PROSE, GUILD_COMMUNICA
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        return f"""Hei.\n\nJoukkueesi {recipient.get_firstname()} ({recipient.get_lastname()}) ilmoittautui onnistuneesti killan kyykkään 2024."""


_form_name = make_form_name(__file__)


def _get_quotas() -> List[Quota]:
    return [
        Quota.default_quota(30, 0)
    ]

def _make_attribute_team_name(validators: Iterable = None):
    validators += [Length(min=1, max=100)]
    return StringAttribute("firstname", "Joukkueen nimi", "Joukkueen nimi", 100, validators=validators)

def _make_attribute_team_abreviation(validators: Iterable = None):
    validators += [Length(min=1, max=25)]
    return StringAttribute("lastname", "Joukkueen lyhenne", "lyhenne", 10, validators=validators)

def _make_attribute_team_captain(validators: Iterable = None):
    return StringAttribute("captain_name", "Kapteenin nimi", "Kapteenin nimi", 100, validators=validators)

def _make_attribute_team_captain_email(validators: Iterable = None):
    validators += [Email()]
    return StringAttribute("email", "Kapteenin sähköposti", "Sähköposti", 100, validators=validators)

def _make_attribute_team_captain_phonenumber(validators: Iterable = None):
    return StringAttribute("phone_number", "Kapteenin puhelinnumero", "puhelinnumero", 100, validators=validators)

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
participant_attributes = [
    _make_attribute_team_name(validators=[InputRequired()]),
    _make_attribute_team_abreviation(validators=[InputRequired()]),
    _make_attribute_team_captain(validators=[InputRequired()]),
    _make_attribute_team_captain_email(validators=[InputRequired()]),
    _make_attribute_team_captain_phonenumber(validators=[InputRequired()])
]

optional_participant_attributes = []

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]
_types = make_types(participant_attributes, optional_participant_attributes, other_attributes, 1, 1, _form_name)

_event = Event('Killan kyykkä 2024', datetime(2024, 1, 9, 12, 00, 00),
               datetime(2024, 1, 21, 23, 59, 59), _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)
