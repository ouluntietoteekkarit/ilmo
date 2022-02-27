from __future__ import annotations

from enum import Enum
from typing import Collection, Iterable, Type, List, Tuple

from app.form_lib.forms import FormTypeFactory
from app.form_lib.guilds import Guild
from app.form_lib.lib import BaseAttribute, TypeContainer, Quota
from app.form_lib.models import DbTypeFactory


def make_types(required_participant_attributes: Collection[BaseAttribute],
               optional_participant_attributes: Collection[BaseAttribute],
               other_attributes: Collection[BaseAttribute],
               required_participant_count: int,
               optional_participant_count: int,
               form_name: str) -> TypeContainer:

    factories = {
        'form_type': FormTypeFactory(required_participant_attributes, optional_participant_attributes,
                                     other_attributes, required_participant_count,
                                     optional_participant_count),
        'model_type': DbTypeFactory(required_participant_attributes, optional_participant_attributes,
                                    other_attributes, required_participant_count,
                                    optional_participant_count, form_name)
    }
    types = {}
    for name, factory in factories.items():
        types[name] = factory.make_type()

    return TypeContainer(**types)


def choices_to_enum(form_name: str, enum_name: str, values: Iterable[str]) -> Type[Enum]:
    name = '{}_{}'.format(form_name, enum_name)
    enum_type: Type[Enum] = Enum(name, values)
    return enum_type


def get_str_choices(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


def get_guild_choices(guilds: Iterable[Guild]) -> list:
    choices = []
    for guild in guilds:
        choices.append((guild.get_name(), guild.get_name()))
    return choices


def get_quota_choices(quotas: Iterable[Quota]):
    choices = []
    for quota in quotas:
        choices.append((quota.get_name(), quota.get_name()))
    return choices