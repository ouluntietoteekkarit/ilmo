from __future__ import annotations
from datetime import datetime
from typing import List

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.lib import BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_phone_number, make_attribute_departure_location, make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_telegram


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
        quota = recipient.get_quota()
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Olet varasijalla.",
                "Jos fuculle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
                "\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi tai telegramissa @esari2"
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, " ", lastname,
                "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location, "\nKiintiö: ", quota,
                "\nTelegram: ", telegram, "\n",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
                "\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi tai telegramissa @esari2"
            ])


_form_name = make_form_name(__file__)

_PARTICIPANT_FUKSI = 'Fuksi'
_PARTICIPANT_TUTOR = 'Tutor'
_PARTICIPANT_BOARD_MEMBER = 'Hallitus'
_PARTICIPANT_KULTTUURISIHTEERI = 'Kulttuurisihteeri'
_PARTICIPANT_OTHER = 'Muu'

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'

_registration_start = datetime(2023, 10, 3, 13, 37, 0)
_registration_end = datetime(2023, 10, 10, 23, 59, 59)

def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(_PARTICIPANT_FUKSI, 100, 20),
        Quota(_PARTICIPANT_TUTOR, 15, 0),
        Quota(_PARTICIPANT_BOARD_MEMBER, 10, 0),
        Quota(_PARTICIPANT_KULTTUURISIHTEERI, 1, 0),
        Quota(_PARTICIPANT_OTHER, 0, 100)
    ]

_DepartureLocationEnum = choices_to_enum(_form_name, 'departure_location', _get_departure_stops())
_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    make_attribute_phone_number(),
    make_attribute_telegram(),
    make_attribute_departure_location(_DepartureLocationEnum),
    make_attribute_quota(_QuotaEnum)
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('OTiTin Fuksicursio 2023',  _registration_start, _registration_end, _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)



