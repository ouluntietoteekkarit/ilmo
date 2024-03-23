from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Dict, Collection, Iterable, Type

from wtforms.validators import InputRequired, Email

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.quota import Quota
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import GUILD_OTIT
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_departure_location, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_telegram, make_attribute_phone_number
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "KMP -24"
_is_enabled = True
_start_date = datetime(2024, 3, 25, 13, 37, 00)
_end_date   = datetime(2025, 3, 31, 23, 59, 00)

class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname          = recipient.get_firstname()
        lastname           = recipient.get_lastname()
        email              = recipient.get_email()
        telegram           = recipient.get_telegram()
        phone_number       = recipient.get_phone_number()
        departure_location = recipient.get_departure_location()

        result = ""
        if reserve:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin KMP:lle. Olet varasijalla. ",
                "Jos KMP:lle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin KMP:lle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email,
                "\nPuhelinnumero: ", phone_number,
                "\nTelegram: ", telegram,
                "\nLähtöpaikka: ", departure_location,
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi."
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 48, 100),
    ]

_DepartureEnum = choices_to_enum(_form_name,
                                 "departure",
                                 ["Yliopisto (X-oven edestä)",
                                  "Tuira (Merikoskenkadun bussipysäkki)",
                                  "Keskusta (Linja-autoasema)"]);

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_telegram(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_departure_location(_DepartureEnum, validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event(_event_name,
               _start_date,
               _end_date,
               _get_quotas(),
               _types.asks_name_consent())

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
