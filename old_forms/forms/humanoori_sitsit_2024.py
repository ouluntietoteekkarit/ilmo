from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Iterable, Type

from wtforms.validators import InputRequired

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_lastname, make_attribute_firstname, make_attribute_email, \
    make_attribute_quota, make_attribute_privacy_consent, make_attribute_name_consent, make_attribute_allergies
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_liquor, \
    make_attribute_usual_sitsi_wine, get_usual_sitsi_wines, get_usual_sitsi_liquors, get_usual_sitsi_drinks, \
    make_enum_usual_sitsi_drink, make_enum_usual_sitsi_liquor, make_enum_usual_sitsi_wine
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.guilds import GUILD_OTIT, GUILD_PROSE, GUILD_COMMUNICA
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut humanöörisitseille. Olet varasijalla.",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä pepeministeri@otit.fi."
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                """\nOlet ilmoittautunut humanöörisitseille. Sitsit järjestetään Walhallassa 20.2.2024 klo 18:00 alkaen.
Sitsien jatkoja varten mukaan OMPx2.

Jos tulee kysyttävää, voit olla sähköpostitse yhteydessä pepeministeri@otit.fi.
Älä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."""
            ])


_form_name = make_form_name(__file__)

_r_start = datetime(2024, 1, 1, 8, 0, 0)
_r_end = datetime(2024, 2, 11, 23, 59, 59)

_r_start_other = datetime(2024, 2, 9, 12, 0, 0)
_r_end_other = datetime(2024, 2, 11, 23, 59, 59)

def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 33, 100, _r_start, _r_end),
        Quota(GUILD_PROSE, 33, 100, _r_start, _r_end),
        Quota(GUILD_COMMUNICA, 33, 100, _r_start, _r_end),
        Quota("Muu", 0, 100, _r_start_other, _r_end_other),
    ]


def _make_attribute_seating_preference(validators: Iterable = None):
    return StringAttribute('seating_preference', 'Pyötäseuratoive', 'Pyötäseuratoive', 100, validators=validators)


_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_DrinkEnum = make_enum_usual_sitsi_drink(_form_name)
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_sitsi_wine(_form_name)

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
] + [
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_seating_preference()
]

optional_participant_attributes = participant_attributes

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]
_types = make_types(participant_attributes, optional_participant_attributes, other_attributes, 1, 1, _form_name)

_event = Event('Humanöörisitsit', _r_start, _r_end, _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)

