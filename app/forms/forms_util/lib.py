from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Union, Callable, Any, Type

from app.forms.forms_util.form_controller import Quota


class TypeFactory(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def makeFormClass(self):
        pass

    @abstractmethod
    def makeModelClass(self):
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


class BaseAttachable(ABC):
    def __init(self, attribute_name: str, getter: Union[Callable[[Any], Any], None]):
        self._attribute_name = attribute_name
        self._getter = getter

    def get_attribute_name(self) -> str:
        return self._attribute_name

    def attach_to(self, component: Type[BaseFormComponent]) -> Type[BaseFormComponent]:
        setattr(component, self._attribute_name, self._make_field_value())
        if self._getter:
            setattr(component, self._getter.__name__, self._getter)

    @abstractmethod
    def _make_field_value(self) -> Any:
        pass
