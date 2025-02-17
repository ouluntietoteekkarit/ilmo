from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Dict, Collection, Iterable, Type

from wtforms.validators import InputRequired, Email, Length

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.quota import Quota
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
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

_event_name = "Rugby trial session"
_is_enabled = True
_start_date = datetime(2025, 2, 17, 13, 37, 00)
_end_date   = datetime(2025, 3, 5, 23, 59, 59)

class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname          = recipient.get_firstname()
        lastname           = recipient.get_lastname()
        email              = recipient.get_email()

        if reserve:
            result = ' '.join([
                f"Greetings, {firstname}!",
                "\nYou have registered for the OTiT rugby trial session. You are on the waiting list.",
                "If spots become available due to cancellations, you may be contacted.",
                "\n\nThis is an automated message, do not reply to this email."
            ])
        else:
            result = ' '.join([
                f"Greetings, {firstname}!",
                "\nYou have registered for the OTiT rugby trial session. The session will be held in Ouluhalli on March 10th at 8 PM.",
                "\n\nHere is the information you provided:",
                "\nName: ", firstname, lastname,
                "\nEmail: ", email,
                "\nTelegram: ", recipient.get_telegram(),
                "\n\nWhat to bring with you?",
                "\n- Sneakers or football boots",
                "\n- Sweatpants or shorts",
                "\n- T-shirt",
                "\n- Mouthguard (if you have one)",
                "\n- Water bottle",
                "\n- Clothes that can handle a little wear and tear.",
                "\n\nIf you have any questions, please contact us via email at urheiluministeri@otit.fi.",
                "\n\nThis is an automated message, do not reply to this email."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota('OTiT', 30, 20),
    ]

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_telegram(validators=[InputRequired()]),
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
               _types.asks_name_consent(),
               True)

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)

