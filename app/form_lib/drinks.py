from enum import Enum
from typing import List, Iterable, Type

from app.form_lib.lib import EnumAttribute
from app.form_lib.util import choices_to_enum

DRINK_ALCOHOLIC = 'Alkoholillinen (Alcoholic)'
DRINK_BEER = 'Olut (Beer)'
DRINK_CIDER = 'Siideri (Cider)'
DRINK_LONG_DRINK = 'Lonkero (Long drink)'
DRINK_NON_ALCOHOLIC = 'Alkoholiton (Non-alcoholic)'
DRINK_RED_WINE = 'Punaviini (Red wine)'
DRINK_WHITE_WINE = 'Valkoviini (White wine)'


def get_usual_sitsi_drinks() -> List[str]:
    return [
        DRINK_BEER,
        DRINK_CIDER,
        DRINK_NON_ALCOHOLIC
    ]

def get_usual_sitsi_drinks_ex() -> List[str]:
    return [
        DRINK_BEER,
        DRINK_CIDER,
        DRINK_LONG_DRINK,
        DRINK_NON_ALCOHOLIC
    ]


def get_usual_sitsi_wines() -> List[str]:
    return [
        DRINK_RED_WINE,
        DRINK_WHITE_WINE,
        DRINK_NON_ALCOHOLIC
    ]

def get_usual_humanisti_sitsi_wines() -> List[str]:
    return [
        DRINK_ALCOHOLIC,
        DRINK_NON_ALCOHOLIC
    ]


def get_usual_sitsi_liquors() -> List[str]:
    return [
        DRINK_ALCOHOLIC,
        DRINK_NON_ALCOHOLIC
    ]

def get_usual_avec_drinks() -> List[str]:
    return [
        "Jaloviina (Jaloviina)",
        "Kermalikööri (Cream liqueur)",
        "Alkoholiton (Non-alcoholic)",
    ]

def make_enum_usual_sitsi_drink(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'drink', get_usual_sitsi_drinks())

def make_enum_usual_sitsi_drink_ex(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'drink', get_usual_sitsi_drinks_ex())

def make_enum_usual_sitsi_wine(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'wine', get_usual_sitsi_wines())

def make_enum_usual_humanisti_sitsi_wine(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'wine2', get_usual_humanisti_sitsi_wines())


def make_enum_usual_sitsi_liquor(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'liquor', get_usual_sitsi_liquors())

def make_enum_usual_avec_drink(form_name: str) -> Type[Enum]:
    return choices_to_enum(form_name, 'avec_drink', get_usual_avec_drinks())

def make_attribute_usual_sitsi_drink(drink_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('drink', 'Juoma | Mild drink', 'Juoma', drink_enum, validators=validators)

def make_attribute_usual_sitsi_wine(wine_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('wine', 'Viini | Wine', 'Viini', wine_enum, validators=validators)

def make_attribute_usual_humanisti_sitsi_wine(wine_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('wine', 'Viini', 'Viini', wine_enum, validators=validators)

def make_attribute_usual_sitsi_liquor(liquor_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('liquor', 'Viinakaato | Shot', 'Viinakaato', liquor_enum, validators=validators)

