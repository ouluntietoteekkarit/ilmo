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
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_irc_name
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Sulkapalloturnaus"
_is_enabled = False
_start_date = datetime(2024, 3, 27, 12, 00, 00)
_end_date   = datetime(2025, 4, 3, 23, 59, 00)

class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:

        result = ""
        if reserve:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin sulkapalloturnaukseen. Olet varasijalla. ",
                "Jos peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin sulkapalloturnaukseen. "
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä urheiluministeri@otit.fi"
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 18, 100),
    ]

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_irc_name(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
]

avec_attributes = participant_attributes

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, avec_attributes, other_attributes, 1, 1, _form_name)

_event = Event(_event_name,
               _start_date,
               _end_date,
               _get_quotas(),
               _types.asks_name_consent())

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
