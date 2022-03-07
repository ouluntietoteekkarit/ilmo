from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Iterable, Type

from wtforms.validators import InputRequired

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_lastname, make_attribute_firstname, make_attribute_email, \
    make_attribute_quota, make_attribute_privacy_consent, make_attribute_name_consent, make_attribute_allergies
from app.form_lib.form_controller import FormController, Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import StringAttribute, EnumAttribute, Quota, BaseParticipant
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
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä joensuu@otit.fi"
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                """\nOlet ilmoittautunut humanöörisitseille. Sitsit järjestetään Walhallassa 14.3. klo 18:00 alkaen.

Tässä vielä maksuohjeet:
Maksettava summa on 23€. 46€ jos osallistut avecin kanssa. Maksu tapahtuu tilisiirrolla
Communica ry:n tilille FI52 5741 3620 5641 27. Kirjoita viestikenttään oma nimesi, avecisi 
nimi ja \"humanöörisitsit\". Maksun eräpäivä on 14.3.2022.

Sitsien jatkoja varten mukaan OMPx2

Jos tulee kysyttävää, voit olla sähköpostitse yhteydessä joensuu@otit.fi
Älä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."""
            ])


_form_name = make_form_name(__file__)

_DRINK_ALCOHOLIC = 'Alkoholillinen'
_DRINK_BEER = 'Olut'
_DRINK_CIDER = 'Siideri'
_DRINK_NON_ALCOHOLIC = 'Alkoholiton'
_DRINK_RED_WINE = 'Punaviini'
_DRINK_WHITE_WINE = 'Valkoviini'


def _get_drinks() -> List[str]:
    return [
        _DRINK_BEER,
        _DRINK_CIDER,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_liquors() -> List[str]:
    return [
        _DRINK_ALCOHOLIC,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_wines() -> List[str]:
    return [
        _DRINK_RED_WINE,
        _DRINK_WHITE_WINE,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 30, 10),
        Quota(GUILD_PROSE, 30, 10),
        Quota(GUILD_COMMUNICA, 30, 10),
    ]


def _make_attribute_drink(drink_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('drink', 'Juoma', 'Juoma', drink_enum, validators=validators)


def _make_attribute_liquor(liquor_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('liquor', 'Viinakaato', 'Viinakaato', liquor_enum, validators=validators)


def _make_attribute_wine(wine_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('wine', 'Viini', 'Viini', wine_enum, validators=validators)


def _make_attribute_searing_preference(validators: Iterable = None):
    return StringAttribute('seating_preference', 'Pyötäseuratoive', 'Pyötäseuratoive', 100, validators=validators)


_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_DrinkEnum = choices_to_enum(_form_name, 'drink', _get_drinks())
_LiquorEnum = choices_to_enum(_form_name, 'liquor', _get_liquors())
_WineEnum = choices_to_enum(_form_name, 'wine', _get_wines())

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
] + [
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    _make_attribute_drink(_DrinkEnum, validators=[InputRequired()]),
    _make_attribute_liquor(_LiquorEnum, validators=[InputRequired()]),
    _make_attribute_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_searing_preference()
]

optional_participant_attributes = participant_attributes

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]
_types = make_types(participant_attributes, optional_participant_attributes, other_attributes, 1, 1, _form_name)

_event = Event('Humanöörisitsit', datetime(2021, 2, 21, 12, 00, 00),
               datetime(2023, 3, 6, 23, 59, 59), _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)

