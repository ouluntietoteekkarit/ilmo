from datetime import datetime
from enum import Enum
from typing import List, Iterable, Type

from wtforms.validators import InputRequired

from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_allergies, make_attribute_quota, make_attribute_name_consent, make_attribute_privacy_consent
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_wine, \
    make_attribute_usual_sitsi_liquor, make_enum_usual_sitsi_drink, make_enum_usual_sitsi_liquor, \
    make_enum_usual_sitsi_wine
from app.form_lib.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations
from app.form_lib.lib import Quota, BaseParticipant, EnumAttribute
from app.form_lib.forms import RegistrationForm
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices
from app.form_lib.models import RegistrationModel


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        return ""


_form_name = make_form_name(__file__)


def _get_quotas() -> List[Quota]:
    return [
        Quota('Fuksi', 100, 0),
        Quota('Pro', 8, 0),
        Quota('Hallitus', 11, 0),
        Quota('Muu', 0, 0)
    ]


_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_DrinkEnum = make_enum_usual_sitsi_drink(_form_name)
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_sitsi_wine(_form_name)

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies (),

]
optional_participant_attributes = []
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('Fuksisitsit', datetime(2022, 8, 29, 12, 00, 00),
               datetime(2022, 9, 4, 23, 59, 59), _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)
