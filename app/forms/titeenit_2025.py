from __future__ import annotations

from datetime import datetime
from typing import List, Iterable

from wtforms.validators import InputRequired, Length, Email

from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_departure_location, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_allergies, make_attribute_telegram, make_attribute_phone_number
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


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()
        phone = recipient.get_phone_number()
        tg = recipient.get_telegram()
        departure = recipient.get_departure_location()
        allergies = recipient.get_allergies()

        if reserve:
            return f"""Tervehdys, {firstname} {lastname}!
            
            Olet ilmoittautunut OTiT:n Titeeni-KMP:lle kohti lappeen Rantoja. Olet varasijalla.
            Jos KMP:lle jää jostain syystä vapaita paikkoja, sinuun ollaan yhteydessä.
            
            Tässä vielä ilmoittamasi tiedot:
            Etunimi: {firstname}
            Sukunimi: {lastname}
            Sähköposti: {email}
            Puhelinnumero: {phone}
            Telegram: {tg}
            Lähtöpaikka: {departure}
            Allergiat: {allergies}
            
            Jos tulee kysyttävää, voit lähettää viestiä sähköpostitse kulttuuriministeri@otit.fi tai Telegramissa @jukeboxxxi.
            Tämä on automaattinen sähköposti, älä vastaa tähän viestiin.
            -----
            Greetings, {firstname} {lastname}!
            
            You have signed up for OTiT's Titeeni-KMP excursion towards lappeen Ranta. You are on the waiting list.
            If there are any free spots for the excursion, you will be contacted.
            
            Here are the details you provided:
            First name: {firstname}
            Last name: {lastname}
            Email: {email}
            Phone number: {phone}
            Telegram: {tg}
            Departure location: {departure}
            Allergies: {allergies}
            
            If you have any questions, you can send an email to kulttuuriministeri@otit.fi or contact @jukeboxxxi on Telegram.
            This is an automated email, do not reply to this message."""
        else:
            return f"""Tervehdys, {firstname} {lastname}!
            Olet ilmoittautunut OTiT:n Titeeni-KMP:lle kohti lappeen Rantoja. Reissuun lähdetään perjantaina 14.3.2025.
            Excun aikataulu, maksuohjeet ja muut tiedot tarkentuvat myöhemmin.
            
            Tässä vielä ilmoittamasi tiedot:
            Etunimi: {firstname}
            Sukunimi: {lastname}
            Sähköposti: {email}
            Puhelinnumero: {phone}
            Telegram: {tg}
            Lähtöpaikka: {departure}
            Allergiat: {allergies}
            
            Maksutiedot tiedotetaan myöhemmin.
            
            Jos tulee kysyttävää, voit lähettää viestiä sähköpostitse kulttuuriministeri@otit.fi tai Telegramissa @jukeboxxxi.
            
            Tämä on automaattinen sähköposti, älä vastaa tähän viestiin.
            -----
            Greetings, {firstname} {lastname}!
            
            You have signed up for OTiT's Titeeni-KMP excursion towards lappeen Ranta. The trip will start on Friday, 14th of March, 2025.
            The schedule, payment instructions and other details for the excursion will be provided later.
            
            Here are the details you provided:
            First name: {firstname}
            Last name: {lastname}
            Email: {email}
            Phone number: {phone}
            Telegram: {tg}
            Departure location: {departure}
            Allergies: {allergies}
            
            If you have any questions, you can send an email to kulttuuriministeri@otit.fi or contact @jukeboxxxi on Telegram.
            This is an automated email, do not reply to this message. """


def _make_attribute_scared():
    txt = "Pelottaako? | Are you scared?"
    return BoolAttribute('is_scared', txt, "Pelottaa / I'm scared")

def _make_attribute_weight(validators: Iterable = None):
    txt = "Paljonko lappeen Ranta painaa ilman kirvestä? | How much does lappeen Ranta weigh without the Titeeni axe?"
    return StringAttribute('weight', txt, "Pelottaa", 20, validators=validators)


def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 48, 10),
        Quota("Muu (Others)", 8, 10),
    ]

def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]

_form_name = make_form_name(__file__)

_DEPARTURE_BUS_STOP_UNI       = 'Yliopisto (X2-oven edestä) | University (In front of X2)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkatu E1)'
_DEPARTURE_BUS_STATION        = 'Keskusta (Linja-autoasema) | City center (Bus station)'

_DepartureEnum = choices_to_enum(_form_name, 'departure', _get_departure_stops())
_QuotaEnum     = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_telegram(validators=[InputRequired()]),
    make_attribute_departure_location(_DepartureEnum, validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_weight(validators=[InputRequired()]),
    _make_attribute_scared()
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('KotiMaanPitkä 2025 goes Titeenit',
               datetime(2025, 2, 11, 13, 37, 0),
               datetime(2025, 2, 16, 23, 59, 59),
               _get_quotas(),
               _types.asks_name_consent(), True)

_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)
