from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Union, Callable, Any, Type, Dict, Iterable

from app.forms.forms_util.form_controller import Quota


class TypeFactory:
    def __init__(self):
        pass

    def make_form_class(self):
        pass

    def make_model_class(self):
        pass


class AttributeFactory(ABC):

    @abstractmethod
    def make_int_attribute(self) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_string_attribute(self) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_bool_attribute(self) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_datetime_attribute(self) -> BaseAttachableAttribute:
        pass

    @abstractmethod
    def make_list_attribute(self) -> BaseAttachableAttribute:
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


class BaseAttributes(BaseFormComponent):
    """Interface-like class for form's attribute models."""
    pass


class BaseModel(BaseFormComponent):
    """Interface-like class for form's data models."""
    def get_model_attributes(self) -> BaseAttributes:
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
    def __init(self, attribute_name: str, getter: Union[Callable[[Any], Any], None]):
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
    def build(self, base_type: Type[BaseFormComponent] = None) -> Type[BaseFormComponent]:
        pass

    def _do_build(self, base_type: Type[BaseFormComponent], required: Dict[str, bool]):
        for field in self._fields:
            field.attach_to(base_type)

            if field.get_attribute_name() in required:
                required[field.get_attribute_name()] = True

        for attr, value in required.items():
            if not value:
                raise Exception(attr + "is a mandatory attribute of " + base_type.__name__)

class BaseAttributeParameters(ABC):
