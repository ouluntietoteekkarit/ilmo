from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Dict, Collection, Iterable, Type

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.quota import Quota
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import GUILD_SIK, GUILD_OTIT
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, make_attribute_phone_number,\
    make_attribute_quota, make_attribute_departure_location, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_allergies
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant, BoolAttribute 
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        if reserve:
            return """{}Olet ilmoittautunut OTiTin KMP:lle. Olet varasijalla. 
Jos KMP:lle jää jostain syystä vapaita paikkoja, sinuun voidaan olla yhteydessä.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))
        else:
            return """{}Olet ilmoittautunut OTiTin KMP:lle. KMP järjestetään 17.3.2023 - 19.3.2023 Turussa.

Maksutiedot tiedotetaan myöhemmin.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))


def _make_attribute_phone_or_tg(validators: Iterable = None):
    return StringAttribute('phone_tg', "Puhelinnumero tai Telegram-käyttäjänimi", 'Puhelinnumero/tg', 100, validators=validators)



def _make_attribute_accommodation():
    txt = "En majoitu yhteismajoituksessa"
    return BoolAttribute('accommodation', txt, 'Oma majoitus')

def _make_attribute_scared():
    txt = "Pelottaako?"
    return BoolAttribute('is_scared', txt, "Pelottaa")


def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 47, 10),
        Quota(GUILD_SIK, 10, 10),
    ]

def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]

_form_name = make_form_name(__file__)

_DEPARTURE_BUS_STOP_UNI       = 'Yliopisto (X-oven edestä)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkadun bussipysäkki)'
_DEPARTURE_BUS_STATION        = 'Keskusta (Linja-autoasema)'

_DepartureEnum = choices_to_enum(_form_name, 'departure', _get_departure_stops())
_QuotaEnum     = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    _make_attribute_phone_or_tg(),
    make_attribute_departure_location(_DepartureEnum),
    make_attribute_quota(_QuotaEnum),
    make_attribute_allergies(),
    _make_attribute_accommodation(),
    _make_attribute_scared(),
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('OTiT KMP/Titeenit',
               datetime(2023, 2, 16, 0, 0, 0),
               datetime(2023, 2, 26, 23, 59, 59),
               _get_quotas(),
               _types.asks_name_consent())

_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)

