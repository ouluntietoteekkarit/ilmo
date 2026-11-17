from __future__ import annotations
from datetime import datetime
from typing import List

from wtforms.validators import InputRequired, Length

from app.email import make_greet_line
from app.form_lib.form_controller import FormController
from app.form_lib.quota import Quota
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.common_attributes import (
    make_attribute_firstname,
    make_attribute_lastname,
    make_attribute_email,
    make_attribute_quota,
    make_attribute_name_consent,
    make_attribute_privacy_consent,
    make_attribute_allergies,
    make_attribute_binding_registration_consent,
)
from app.form_lib.drinks import (
    make_attribute_usual_sitsi_drink,
    make_attribute_usual_sitsi_liquor,
    make_attribute_usual_sitsi_wine,
    make_enum_usual_sitsi_drink,
    make_enum_usual_sitsi_liquor,
    make_enum_usual_sitsi_wine,
)
from app.form_lib.lib import BaseParticipant, StringAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "TST-sitsit"
_is_enabled = True
_start_date = datetime(2026, 11, 15, 12, 0, 0)
_end_date = datetime(2026, 11, 22, 14, 0, 0)


def _make_attribute_seating_preference() -> StringAttribute:
    return StringAttribute(
        "seating_preference",
        "Vieruskaveritoive | Seating preference",
        "Vieruskaveritoive",
        100,
    )


class _Controller(FormController):
    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        greeting = make_greet_line(recipient)
        if reserve:
            return " ".join(
                [
                    greeting,
                    "\nOlet ilmoittautunut TST-sitseille varasijalle.",
                    "Jos paikkoja vapautuu, sinuun voidaan olla yhteydessä.",
                    (
                        "\n\nJos tulee kysyttävää, voit olla yhteydessä pepeministeri@otit.fi."
                        "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene mihinkään."
                    ),
                ]
            )
        return " ".join(
            [
                greeting,
                "\nOlet ilmoittautunut TST-sitseille.",
                "\n\nJos tulee kysyttävää, voit olla yhteydessä pepeministeri@otit.fi.",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene mihinkään.",
            ]
        )


def _get_quotas() -> List[Quota]:
    return [
        Quota('SIK', 20, 10),
        Quota('OLTO', 16, 10),
        Quota('OTiT', 20, 10),
        Quota('Blanko', 20, 10),
        Quota('Proffa', 3, 10),
        Quota('Sere', 3, 0)
    ]


_QuotaEnum = choices_to_enum(
    _form_name,
    'quota',
    get_quota_choices(_get_quotas()),
)

_DrinkEnum = make_enum_usual_sitsi_drink(_form_name)
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_sitsi_wine(_form_name)

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_seating_preference(),
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()]),
    make_attribute_binding_registration_consent("", validators=[InputRequired()]),
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event(
    _event_name,
    _start_date,
    _end_date,
    _get_quotas(),
    _types.asks_name_consent(),
)

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
