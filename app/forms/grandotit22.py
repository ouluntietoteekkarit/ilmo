from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Dict, Collection, Iterable, Type

from wtforms.validators import InputRequired, Optional

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.quota import Quota
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_name_consent, make_attribute_privacy_consent, make_attribute_allergies
from app.form_lib.lib import StringAttribute, BaseParticipant, IntAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        if reserve:
            return """{}Olet ilmoittaunut Grand OTiT iltatapahtumaan. Olet varasijalla. Teihin voidaan olla
yhteydessä, mikäli paikkoja vapautuu.

Kysymykset tapahtumaan liittyen voi lähettää osoitteeseen alumnivastaava@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään.""".format(make_greet_line(recipient))

        else:
            return """{}Olet ilmoittautunut Grand OTiT iltatapahtumaan, joka järjestetään 28.5. klo 17.00 alkaen Teekkaritalolla 
(Kalervontie 7 Oulu). Tapahtuman maksutiedot toimitetaan myöhemmin lähempänä ajankohtaa. Maksu 
tulee olemaan 10-20€, riippuen lopullisesta osallistujamäärästä.

Kysymykset tapahtumaan liittyen voi lähettää osoitteeseen alumnivastaava@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään.""".format(make_greet_line(recipient))


def _get_quotas() -> List[Quota]:
    return [
        Quota.default_quota(70, 80)
    ]


_form_name = make_form_name(__file__)


def _make_attribute_speech(validators: Iterable = None):
    return StringAttribute('speaker', 'Puheen pitäjän nimi', 'Puheen pitäjän nimi', 100, validators=validators)


def _make_attribute_board_year(validators: Iterable = None):
    return StringAttribute('board_year', 'Hallitusvuosi', 'Hallitusvuosi', 50, validators=validators)


participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
] + [
    _make_attribute_board_year(),
    make_attribute_allergies(),
    _make_attribute_speech(),
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('Grand OTiT', datetime(2022, 2, 25, 13, 37, 00),
               datetime(2022, 5, 15, 23, 59, 59), _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)

