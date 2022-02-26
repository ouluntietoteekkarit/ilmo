from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union, Callable, Any, Type, Dict, Iterable, Iterator, Collection, TypeVar, Generic

from app.form_lib.form_controller import Quota

ATTRIBUTE_NAME_FIRSTNAME = 'firstname'
ATTRIBUTE_NAME_LASTNAME = 'lastname'
ATTRIBUTE_NAME_EMAIL = 'email'
ATTRIBUTE_NAME_QUOTA = 'quota'
ATTRIBUTE_NAME_PHONE_NUMBER = 'phone_number'
ATTRIBUTE_NAME_DEPARTURE_LOCATION = 'departure_location'
ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS = 'required_participants'
ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS = 'optional_participants'
ATTRIBUTE_NAME_OTHER_ATTRIBUTES = 'other_attributes'
ATTRIBUTE_NAME_PRIVACY_CONSENT = 'privacy_consent'
ATTRIBUTE_NAME_NAME_CONSENT = 'show_name_consent'
ATTRIBUTE_NAME_BINDING_REGISTRATION_CONSENT = 'binding_registration_consent'


class TypeFactory(ABC):
    def __init__(self,
                 required_participant_attributes: Collection[BaseAttribute],
                 optional_participant_attributes: Collection[BaseAttribute],
                 other_attributes: Collection[BaseAttribute],
                 required_participant_count: int,
                 optional_participant_count: int):
        self._required_participant_attributes = required_participant_attributes
        self._optional_participant_attributes = optional_participant_attributes
        self._other_attributes = other_attributes
        self._required_participant_count = required_participant_count
        self._optional_participant_count = optional_participant_count

    @abstractmethod
    def make_type(self) -> Type[BaseModel]:
        pass


class AttributeFactory(ABC):

    @abstractmethod
    def make_int_attribute(self, params: IntAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_string_attribute(self, params: StringAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_bool_attribute(self, params: BoolAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_datetime_attribute(self, params: DatetimeAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_enum_attribute(self, params: EnumAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_list_attribute(self, params: ListAttribute) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_object_attribute(self, params: ObjectAttribute) -> BaseAttachableAttribute:
        pass


# MEMO: Must not have meta class.
class BaseFormComponent:
    pass


class BaseParticipant(BaseFormComponent):
    """Interface-like class for form's participant models."""
    def get_firstname(self) -> str:
        raise Exception("Not implemented")

    def get_lastname(self) -> str:
        raise Exception("Not implemented")

    def get_email(self) -> str:
        return ''

    def get_quota_name(self) -> str:
        return Quota.default_quota_name()

    def is_filled(self) -> bool:
        return bool(self.get_firstname() and self.get_lastname())


class BaseOtherAttributes(BaseFormComponent):
    """Interface-like class for form's attribute models."""
    pass


class BaseModel(BaseFormComponent):
    """Interface-like class for form's data models."""
    def get_model_attributes(self) -> BaseOtherAttributes:
        raise Exception("Not implemented")

    def get_required_participants(self) -> List[BaseParticipant]:
        raise Exception("Not implemented")

    def get_optional_participants(self) -> List[BaseParticipant]:
        return []

    def get_show_name_consent(self) -> bool:
        return False

    def get_participant_count(self) -> int:
        count = 0
        for p in self.get_required_participants():
            count += int(p.is_filled())

        for p in self.get_optional_participants():
            count += int(p.is_filled())

        return count

    def get_quota_counts(self) -> List[Quota]:
        quotas = []
        for p in self.get_required_participants():
            quotas.append(Quota(p.get_quota_name(), int(p.is_filled())))

        for p in self.get_optional_participants():
            quotas.append(Quota(p.get_quota_name(), int(p.is_filled())))

        return quotas


class BaseAttachableAttribute(ABC):
    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None]):
        self._attribute_name = attribute_name
        self._getter = getter

    def get_attribute_name(self) -> str:
        return self._attribute_name

    def attach_to(self, component: Type[BaseFormComponent]) -> Type[BaseFormComponent]:
        setattr(component, self._attribute_name, self._make_field_value())
        if self._getter:
            setattr(component, self._getter.__name__, self._getter)

        return component

    @abstractmethod
    def _make_field_value(self) -> Any:
        pass


class NullAttachableAttribute(BaseAttachableAttribute):

    def attach_to(self, component: Type[BaseFormComponent]) -> Type[BaseFormComponent]:
        return component

    def _make_field_value(self) -> Any:
        return None


T = TypeVar('T', bound=BaseFormComponent)


class BaseTypeBuilder(ABC):
    def __init__(self):
        self._fields: List[BaseAttachableAttribute] = []

    def reset(self) -> BaseTypeBuilder:
        self._fields = []
        return self

    def add_field(self, field: BaseAttachableAttribute) -> BaseTypeBuilder:
        self._fields.append(field)
        return self

    def add_fields(self, fields: Iterable[BaseAttachableAttribute]) -> BaseTypeBuilder:
        for field in fields:
            self.add_field(field)

        return self

    @abstractmethod
    def build(self, base_type: Type[Generic[T]] = None) -> Type[Generic[T]]:
        pass

    def _do_build(self, base_type: Type[Generic[T]], required: Dict[str, bool]) -> Type[Generic[T]]:
        for field in self._fields:
            field.attach_to(base_type)

            if field.get_attribute_name() in required:
                required[field.get_attribute_name()] = True

        for attr, value in required.items():
            if not value:
                raise Exception(attr + "is a mandatory attribute of " + base_type.__name__)

        return base_type


class BaseAttribute(ABC):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 **extra: Dict[str, Any]):
        self._attribute = attribute
        self._label = label
        self._short_label = short_label
        self._extra = extra

    def get_attribute(self) -> str:
        return self._attribute

    def get_label(self) -> str:
        return self._label

    def get_short_label(self) -> str:
        return self._short_label

    def get_extra(self) -> Dict[str, Any]:
        return self._extra

    def try_get_extra(self, key: str, default_value: Any) -> Any:
        return self._extra[key] if key in self._extra else default_value


class IntAttribute(BaseAttribute):
    pass


class StringAttribute(BaseAttribute):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 length: int,
                 **extra: Dict[str, Any]):
        super().__init__(attribute, label, short_label, **extra)
        self._length = length

    def get_length(self) -> int:
        return self._length


class BoolAttribute(BaseAttribute):
    pass


class DatetimeAttribute(BaseAttribute):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 datetime_format: str,
                 **extra: Dict[str, Any]):
        super().__init__(attribute, label, short_label, **extra)
        self._datetime_format = datetime_format

    def get_datetime_format(self):
        return self._datetime_format


class EnumAttribute(BaseAttribute):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 enum_type: Type[Enum],
                 **extra: Dict[str, Any]):
        super().__init__(attribute, label, short_label, **extra)
        self._enum_type = enum_type

    def get_enum_type(self):
        return self._enum_type


class ListAttribute(BaseAttribute):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 list_type: Type[BaseFormComponent],
                 count: int,
                 **extra: Dict[str, Any]):
        super().__init__(attribute, label, short_label, **extra)
        self._list_type = list_type
        self._count = count

    def get_list_type(self) -> Type[BaseFormComponent]:
        return self._list_type

    def get_count(self) -> int:
        return self._count


class ObjectAttribute(BaseAttribute):
    def __init__(self,
                 attribute: str,
                 label: str,
                 short_label: str,
                 object_type: Type[BaseFormComponent],
                 **extra: Dict[str, Any]):
        super().__init__(attribute, label, short_label, **extra)
        self._object_type = object_type

    def get_object_type(self) -> Type[BaseFormComponent]:
        return self._object_type


def attributes_to_fields(factory: AttributeFactory,
                         attributes: Iterable[BaseAttribute]
                         ) -> Iterator[BaseAttachableAttribute]:
    for attribute in attributes:
        if isinstance(attribute, IntAttribute):
            yield factory.make_int_attribute(attribute)
        elif isinstance(attribute, StringAttribute):
            yield factory.make_string_attribute(attribute)
        elif isinstance(attribute, BoolAttribute):
            yield factory.make_bool_attribute(attribute)
        elif isinstance(attribute, DatetimeAttribute):
            yield factory.make_datetime_attribute(attribute)
        elif isinstance(attribute, ListAttribute):
            yield factory.make_list_attribute(attribute)
        elif isinstance(attribute, ObjectAttribute):
            yield factory.make_object_attribute(attribute)
        elif isinstance(attribute, EnumAttribute):
            yield factory.make_enum_attribute(attribute)
        else:
            raise Exception("Invalid attribute parameter type. " + str(type(attribute)))


class TypeContainer:
    def __init__(self, model_type, form_type):
        self._model_type = model_type
        self._form_type = form_type

    def get_model_type(self):
        return self._model_type

    def get_form_type(self):
        return self._form_type
