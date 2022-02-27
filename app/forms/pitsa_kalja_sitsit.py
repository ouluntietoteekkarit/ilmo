from __future__ import annotations
from enum import Enum

from datetime import datetime
from typing import List, Type, Iterable

from app.email import EmailRecipient, make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_allergies, make_attribute_privacy_consent, make_attribute_name_consent
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.form_controller import FormController, Event
from app.form_lib.lib import Quota, EnumAttribute
from app.form_lib.util import make_types, choices_to_enum


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool):
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Olet varasijalla. ",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Tässä vielä maksuohjeet: ",
                "\n\n Hinta alkoholillisen juoman kanssa on 20€ ja alkoholittoman juoman ",
                "kanssa 17€. Maksu tapahtuu tilisiirrolla Oulun Tietoteekkarit ry:n tilille ",
                "FI03 4744 3020 0116 87. Kirjoita viestikenttään nimesi, ",
                "Pitsakalja-sitsit sekä alkoholiton tai alkoholillinen valintasi mukaan.",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])

_form_name = make_form_name(__file__)

_DRINK_ALCOHOLIC = 'Alkoholillinen'
_DRINK_NON_ALCOHOLIC = 'Alkoholiton'

_DRINK_ALCOHOLIC_MILD_BEER = 'Olut'
_DRINK_ALCOHOLIC_MILD_CIDER = 'Siideri'

_PIZZA_MEAT = 'Liha'
_PIZZA_CHICKEN = 'Kana'
_PIZZA_VEGETARIAN = 'Vege'


def _get_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_alcoholic_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC_MILD_BEER,
        _DRINK_ALCOHOLIC_MILD_CIDER
    ]


def _get_pizzas() -> List[str]:
    return [
        _PIZZA_MEAT,
        _PIZZA_CHICKEN,
        _PIZZA_VEGETARIAN
    ]


def _make_attribute_alcohol(alcohol_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('alcohol', 'Alkoholillinen/Alkoholiton *', 'Alkoholillinen/Alkoholiton', alcohol_enum, validators=validators)


def _make_attribute_drink_strength(drink_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('drink_strength', 'Mieto juoma *', 'Mieto juoma', drink_enum, validators=validators)


def _make_attribute_pizza(pizza_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('pizza', 'Pitsa *', 'Pitsa', pizza_enum, validators=validators)


_AlcoholEnum = choices_to_enum(_form_name, 'alcohol', _get_drinks())
_DrinkStrengthEnum = choices_to_enum(_form_name, 'drink_strength', _get_alcoholic_drinks())
_PizzaEnum = choices_to_enum(_form_name, 'pizza', _get_pizzas())


participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    _make_attribute_alcohol(_AlcoholEnum),
    _make_attribute_drink_strength(_DrinkStrengthEnum),
    _make_attribute_pizza(_PizzaEnum),
    make_attribute_allergies()
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)
_Form = _types.get_form_type()
_Model = _types.get_model_type()





_event = Event('OTiTin Pitsakaljasitsit', datetime(2021, 10, 26, 12, 00, 00),
               datetime(2021, 11, 9, 23, 59, 59), [Quota.default_quota(60, 30)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)

