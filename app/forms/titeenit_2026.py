from __future__ import annotations

from datetime import datetime
from typing import List, Iterable

from wtforms.validators import InputRequired, Length, Email

from app.form_lib.common_attributes import make_attribute_firstnames, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_departure_location, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_allergies, make_attribute_telegram, make_attribute_phone_number, \
    make_attribute_binding_registration_consent
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import GUILD_OTIT
from app.form_lib.lib import StringAttribute, BaseParticipant, BoolAttribute, IntAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_event_name = "Titeenit 2026"
_is_enabled = True
_start_date = datetime(2026, 2, 20, 13, 37, 00)
_end_date   = datetime(2026, 3, 9, 23, 59, 00)
_form_name = make_form_name(__file__)


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstnames = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()
        phone = recipient.get_phone_number()
        tg = recipient.get_telegram()
        departure = recipient.get_departure_location()
        allergies = recipient.get_allergies()
        other = recipient.get_other()
        
        return f"""Tervehdys, {firstnames} {lastname}!
            
Olet ilmoittautunut OTiT:n Titeeni-KMP:lle kohti Otaniemeä. Reissuun lähdetään perjantaina 13.3.2026 klo 7:00.

Tässä vielä ilmoittamasi tiedot:
Etunimet: {firstnames}
Sukunimi: {lastname}
Sähköposti: {email}
Puhelinnumero: {phone}
Telegram: {tg}
Lähtöpaikka: {departure}
Allergiat: {allergies}
Muu: {other}
        
Muista liittyä reissun Telegram-ryhmään: https://t.me/+u9vicgScm_JjZDM8

Jos tulee kysyttävää, kysy reissun ryhmässä, lähetä sähköpostia kulttuuriministeri@otit.fi tai viestiä Telegramissa @Jykamias.
Tämä on automaattinen sähköposti, älä vastaa tähän viestiin.

-----

Greetings, {firstnames} {lastname}!

You have signed up for OTiT's Titeeni-KMP excursion towards Otaniemi. The trip will start on Friday, 13th of March, 2026 at 7:00.

Here are the details you provided:
First name(s): {firstnames}
Last name: {lastname}
Email: {email}
Phone number: {phone}
Telegram: {tg}
Departure location: {departure}
Allergies: {allergies}
Other: {other}
        
Remember to join the excursion's Telegram group: https://t.me/+u9vicgScm_JjZDM8

If you have any questions, ask in the group, send an email to kulttuuriministeri@otit.fi or contact @Jykamias on Telegram.
This is an automated email, do not reply to this message."""

def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 50, 0),
        Quota("Muu (Others)", 10, 0),
    ]

def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]

_DEPARTURE_BUS_STOP_UNI       = 'Yliopisto (X2-oven edestä) | University (In front of X2)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkatu E1)'
_DEPARTURE_BUS_STATION        = 'Keskusta (Linja-autoasema) | City center (Bus station)'

_DepartureEnum = choices_to_enum(_form_name, 'departure', _get_departure_stops())
_QuotaEnum     = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))

def _make_attribute_other(validators: Iterable = None):
    return StringAttribute('other', 'Muu | Other', 'Muu', 200, validators=validators)

participant_attributes = [
    make_attribute_firstnames(validators=[InputRequired(), Length(max=40)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_telegram(validators=[InputRequired()]),
    make_attribute_departure_location(_DepartureEnum, validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    _make_attribute_other(validators=[InputRequired()]),
    make_attribute_allergies(),
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()]),
    make_attribute_binding_registration_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event(_event_name,
               _start_date,
               _end_date,
               _get_quotas(),
               _types.asks_name_consent(),
               True)

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
