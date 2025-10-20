from datetime import datetime
from typing import List, Union

from wtforms.validators import InputRequired

from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_allergies, make_attribute_quota, make_attribute_name_consent, make_attribute_privacy_consent, \
    make_attribute_binding_registration_consent, make_attribute_phone_number, make_attribute_telegram, \
    make_attribute_departure_location
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import BaseParticipant
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
        phone_number = recipient.get_phone_number()
        telegram = recipient.get_telegram()
        departure_location = recipient.get_departure_location()

        if reserve:
            return f"""Tervehdys, {firstname} {lastname}! Olet ilmoittautunut OTiT:n fuksiexcursiolle. 
Olet varasijalla. Jos excursiolle jää peruutuksien myötä vapaita paikkoja, sinuun voidaan olla yhteydessä.

Tässä vielä ilmoittamasi tiedot:
Nimi: {firstname} {lastname}
Sähköposti: {email}
Puhelinnumero: {phone_number}
Telegram: {telegram}
Lähtöpaikka: {departure_location}

Älä vastaa tähän sähköpostiin, vastaus ei mene mihinkään.
-----
Greetings, {firstname} {lastname}! You have registered for OTiT’s freshman excursion.
You are on the waiting list. If there are cancellations and free spots become available, you may be contacted.
Here are the details you provided:
Name: {firstname} {lastname}
Email: {email}
Phone number: {phone_number}
Telegram: {telegram}
Departure location: {departure_location}

Do not reply to this email, responses will not be received."""
        else:
            return f"""Tervehdys, {firstname} {lastname}! Olet ilmoittautunut OTiT:n fuksiexcursiolle.
Bussi lähtee aikaisin aamulla 31.10., aikataulu tarkentuu lähempänä.
Takaisin Oulussa olemme 1.11. joskus aamulla/päivällä. Bussi lähtee yliopiston X-ovelta. 
Tämän jälkeen kyytiin voi nousta Tuirasta ja linja-autoasemalta.
Excursion kohteessa lämpiää sauna, joten OPMx2.

Tässä vielä ilmoittamasi tiedot:
Nimi: {firstname} {lastname}
Sähköposti: {email}
Puhelinnumero: {phone_number}
Telegram: {telegram}
Lähtöpaikka: {departure_location}

Jos sinulla herää kysymyksiä, voit olla yhteydessä sähköpostitse kulttuuriministeri@otit.fi tai TGssä @jukeboxxxi.
Älä vastaa tähän sähköpostiin, vastaus ei mene mihinkään.
-----
Greetings, {firstname} {lastname}! You have registered for OTiT’s freshman excursion.
The bus departs early in the morning on October 31st, the schedule will be finalized closer to the date.
We will be back in Oulu on November 1st sometime in the morning/afternoon. The bus departs near the X door at the university.
After that, you can board at Tuira and the bus station.
The excursion site has a sauna, so BYOB + towel.

Here are the details you provided:
Name: {firstname} {lastname}
Email: {email}
Phone number: {phone_number}
Telegram: {telegram}
Departure location: {departure_location}

If you have any questions, you can contact us by email at kulttuuriministeri@otit.fi or on Telegram @jukeboxxxi.
Do not reply to this email, responses will not be received."""


_form_name = make_form_name(__file__)

_QUOTA_FUKSI = 'Fuksi (Freshman)'
_QUOTA_TUTOR = 'Tutor'
_QUOTA_LEADER = 'Ryhmänjohtaja'
_QUOTA_OTHER = 'Muu (Other)'

class OtherQuota(Quota):
    def __init__(self, fuksiQuota: Quota, name: str, quota: int, reserve_quota: int = 0,
                 registration_start: Union[datetime, None] = None,
                 registration_end: Union[datetime, None] = None):
        super(OtherQuota, self).__init__(name, quota, reserve_quota, registration_start, registration_end)

        self._fuksiQuota = fuksiQuota

    def get_max_quota(self) -> int:
        return self._fuksiQuota.get_max_quota() - self._fuksiQuota.get_registrations()


def _get_quotas() -> List[Quota]:
    fuksi_quota = Quota(_QUOTA_FUKSI, 100, 20)
    return [
        fuksi_quota,
        Quota(_QUOTA_TUTOR, 16, 0),
        Quota(_QUOTA_LEADER, 4, 0),
        OtherQuota(fuksi_quota, _QUOTA_OTHER, 0, 100)
    ]


_registration_start = datetime(2025, 10, 21, 13, 37, 0)
_registration_end = datetime(2025, 10, 26, 23, 59, 59)

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto (University)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkatu E1 bus stop)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema (Bus station)'

def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]

_DepartureLocationEnum = choices_to_enum(_form_name, 'departure_location', _get_departure_stops())

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_telegram(validators=[InputRequired()]),
    make_attribute_departure_location(_DepartureLocationEnum, validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_allergies()
]
optional_participant_attributes = []
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()]),
    make_attribute_binding_registration_consent("", validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('Fuksiexcursio 2025', _registration_start, _registration_end, _get_quotas(), _types.asks_name_consent(), hide_title=True)
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)

