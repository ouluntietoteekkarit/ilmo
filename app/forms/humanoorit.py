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
    make_attribute_privacy_consent, make_attribute_allergies, make_attribute_phone_number
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_liquor, \
    make_attribute_usual_sitsi_wine, get_usual_sitsi_wines, get_usual_sitsi_liquors, get_usual_sitsi_drinks, \
    make_enum_usual_sitsi_drink_ex, make_enum_usual_sitsi_liquor, make_enum_usual_sitsi_wine
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Humanöörit"
_is_enabled = True
_start_date = datetime(2025, 2, 5, 12, 00, 00)
_end_date   = datetime(2025, 2, 12, 23, 59, 00)

def _make_attribute_seating_preference(validators: Iterable = None):
    return StringAttribute('seating_preference', 'Pyötäseuratoive', 'Pyötäseuratoive', 100, validators=validators)

class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname          = recipient.get_firstname()
        lastname           = recipient.get_lastname()
        email              = recipient.get_email()

        result = ""
        if reserve:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut humanöörisitseille. Olet varasijalla.",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä soteministeri@otit.fi."
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut humanöörisitseille.",
                "\n\nName: ", firstname, lastname,
                "\nEmail: ", email,
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä soteministeri@otit.fi."
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota('OTiT', 33, 10),
        Quota('Communica', 33, 10),
        Quota('Prose', 33, 10),
        Quota('Vieraileva Tähti', 1, 0),
    ]

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

_DrinkEnum = make_enum_usual_sitsi_drink_ex(_form_name) # include lonkero
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_sitsi_wine(_form_name)

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
] + [
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_seating_preference()
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

