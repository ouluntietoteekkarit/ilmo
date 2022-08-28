from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Collection, Iterable, Type, List, Tuple, Callable

from app.form_lib.form_controller import DataTableInfo
from app.form_lib.forms import FormTypeFactory, RegistrationForm
from app.form_lib.guilds import Guild
from app.form_lib.lib import BaseAttribute, AttributeFactory
from app.form_lib.quota import Quota
from app.form_lib.models import DbTypeFactory, RegistrationModel


class TypeInfo:
    def __init__(self, model_type: Type[RegistrationModel],
                 model_factory_method: Callable[[int, int, datetime], RegistrationModel],
                 form_type: Type[RegistrationForm],
                 form_factory_method: Callable[[int, int, datetime], RegistrationForm],
                 data_info: DataTableInfo):
        self._model_type = model_type
        self._model_factory_method = model_factory_method
        self._form_type = form_type
        self._form_factory_method = form_factory_method
        self._data_info = data_info

    def get_model_type(self) -> Type[RegistrationModel]:
        return self._model_type

    def get_model_factory_method(self) -> Callable[[int, int, datetime], RegistrationModel]:
        return self._model_factory_method

    def get_form_type(self) -> Type[RegistrationForm]:
        return self._form_type

    def get_form_factory_method(self) -> Callable[[int, int, datetime], RegistrationForm]:
        return self._form_factory_method

    def get_data_info(self) -> DataTableInfo:
        return self._data_info

    def asks_name_consent(self) -> bool:
        return self._form_type.asks_name_consent


def make_types(required_participant_attributes: Collection[BaseAttribute],
               optional_participant_attributes: Collection[BaseAttribute],
               other_attributes: Collection[BaseAttribute],
               required_participant_count: int,
               optional_participant_count: int,
               form_name: str) -> TypeInfo:

    factories = {
        'form': FormTypeFactory(required_participant_attributes, optional_participant_attributes,
                                other_attributes, required_participant_count,
                                optional_participant_count),
        'model': DbTypeFactory(required_participant_attributes, optional_participant_attributes,
                               other_attributes, required_participant_count,
                               optional_participant_count, form_name)
    }
    data_info = make_data_table_info_from_attributes(required_participant_attributes, optional_participant_attributes,
                                                     other_attributes, required_participant_count,
                                                     optional_participant_count)
    types = {
        'data_info': data_info
    }
    for name, factory in factories.items():
        type_info = factory.make_type()
        types[f'{name}_type'] = type_info[0]
        types[f'{name}_factory_method'] = type_info[1]

    return TypeInfo(**types)


def choices_to_enum(form_name: str, enum_name: str, values: Iterable[str]) -> Type[Enum]:
    name = '{}_{}'.format(form_name, enum_name)
    enum_type: Type[Enum] = Enum(name, {member: member for member in values})
    return enum_type


def get_str_choices(values: Iterable[str]) -> List[str]:
    choices = []
    for val in values:
        choices.append(val)
    return choices


def get_guild_choices(guilds: Iterable[Guild]) -> List[str]:
    choices = []
    for guild in guilds:
        choices.append(guild.get_name())
    return choices


def get_quota_choices(quotas: Iterable[Quota]):
    choices = []
    for quota in quotas:
        choices.append(quota.get_name())
    return choices


def make_data_table_info_from_attributes(
        required_participant_attributes: Iterable[BaseAttribute],
        optional_participant_attributes: Iterable[BaseAttribute],
        other_attributes: Iterable[BaseAttribute],
        max_required_participants: int,
        max_optional_participants: int) -> DataTableInfo:

    require_participant = []
    optional_participant = []
    other = []

    for attribute in required_participant_attributes:
        attribute_getter = AttributeFactory.make_getter_name(attribute.get_attribute())
        require_participant.append((attribute_getter, attribute.get_short_label()))

    for attribute in optional_participant_attributes:
        attribute_getter = AttributeFactory.make_getter_name(attribute.get_attribute())
        optional_participant.append((attribute_getter, attribute.get_short_label()))

    for attribute in other_attributes:
        attribute_getter = AttributeFactory.make_getter_name(attribute.get_attribute())
        other.append((attribute_getter, attribute.get_short_label()))

    return DataTableInfo(require_participant, optional_participant, other,
                         max_required_participants, max_optional_participants)

