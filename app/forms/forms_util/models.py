from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Iterable, Type, Union, Callable, Any

from sqlalchemy import Table, MetaData

from app import db
from .form_controller import Quota


# MEMO: Must have same attribute names as BasicForm
"""
class BasicModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(128))
    privacy_consent = db.Column(db.Boolean())
    show_name_consent = db.Column(db.Boolean(), default=False)
    datetime = db.Column(db.DateTime())

    def get_firstname(self) -> str:
        return self.firstname

    def get_lastname(self) -> str:
        return self.lastname

    def get_email(self) -> str:
        return self.email

    def get_show_name_consent(self) -> bool:
        return self.show_name_consent

    def get_quota_counts(self) -> List[Quota]:
        return [Quota.default_quota(1, 0)]
"""

class BasicParticipantModel(db.Model):
    # MEMO: Default implementations for methods required by system logic.
    #       Exceptions make it easier to spot programming errors.

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


class ModelAttributesModel(db.Model):
    pass


class BasicModel(db.Model):

    def get_model_attributes(self) -> ModelAttributesModel:
        raise Exception("Mandatory model field not implemented.")

    def get_required_participants(self) -> List[BasicParticipantModel]:
        raise Exception("Mandatory model field not implemented.")

    def get_optional_participants(self) -> List[BasicParticipantModel]:
        return []

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


class BaseBuilder(ABC):
    def __init__(self):
        self._columns: List[AttachableColumn] = []

    def reset(self) -> BaseBuilder:
        self._columns = []
        return self

    def add_column(self, column: AttachableColumn) -> BaseBuilder:
        self._columns.append(column)
        return self

    def add_columns(self, columns: Iterable[AttachableColumn]) -> BaseBuilder:
        for column in columns:
            self.add_column(column)

        return self

    @abstractmethod
    def build(self, base_type: Type[db.Model]) -> Type[db.Model]:
        pass


class ModelBuilder(BaseBuilder):

    def build(self, base_type: Type[db.Model]) -> Type[db.Model]:
        pass


class ParticipantModelBuilder(BaseBuilder):

    def build(self, base_type: Type[db.Model]) -> Type[db.Model]:
        pass


class ModelAttributesBuilder(BaseBuilder):

    def build(self, base_type: Type[db.Model]) -> Type[db.Model]:
        pass


class AttachableColumn(ABC):
    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None]):
        self._attribute_name = attribute_name
        self._getter = getter

    def _attach(self, model: Type[db.Model], column: db.Column) -> Type[db.Model]:
        setattr(model, self._attribute_name, column)
        if self._getter:
            setattr(model, self._getter.__name__, self._getter)

        return model

    def get_attribute_name(self) -> str:
        return self._attribute_name

    @abstractmethod
    def attach_to(self, form: Type[db.Model]) -> Type[db.Model]:
        pass


class AttachableStringColumn(AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], length: int):
        super().__init__(attribute_name, getter)
        self._length = length

    def attach_to(self, model: Type[db.Model]) -> Type[db.Model]:
        return self._attach(model, db.Column(db.String(self._length)))


class AttachableIntColumn(AttachableColumn):

    def attach_to(self, model: Type[db.Model]) -> Type[db.Model]:
        return self._attach(model, db.Column(db.Integer))


class AttachableBoolColumn(AttachableColumn):

    def attach_to(self, model: Type[db.Model]) -> Type[db.Model]:
        return self._attach(model, db.Column(db.Boolean()))


class AttachableDatetimeColumn(AttachableColumn):

    def attach_to(self, model: Type[db.Model]) -> Type[db.Model]:
        return self._attach(model, db.Column(db.DateTime()))


class AttachableRelationshipColumn(AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], model_class_name: str):
        super().__init__(attribute_name, getter)
        self._model_class_name = model_class_name

    def attach_to(self, model: Type[db.Model]) -> Type[db.Model]:
        return self._attach(model, db.Column(db.relationship(self._model_class_name)))


class PhoneNumberColumn:
    phone_number = db.Column(db.String(32))

    def get_phone_number(self) -> str:
        return self.phone_number


# MEMO: Must have same attribute names as DepartureBusstopField
class DepartureBusstopColumn:
    departure_busstop = db.Column(db.String(64))

    def get_departure_busstop(self) -> str:
        return self.departure_busstop


# MEMO: Must have same attribute names as GuildField
class GuildColumn:
    guild_name = db.Column(db.String(16))

    def get_guild_name(self) -> str:
        return self.guild_name


# MEMO: Must have same attribute names as BindingRegistrationConsentField
class BindingRegistrationConsentColumn:
    binding_registration_consent = db.Column(db.Boolean())

    def get_binding_registration_consent(self) -> bool:
        return self.binding_registration_consent


def basic_model_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('email', 'email'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('show_name_consent', 'hyväksyn nimen julkaisun'),
        ('datetime', 'pvm')
    ]


def phone_number_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('phone_number', 'puhelinnumero')
    ]


def guild_name_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('guild_name', 'kilta')
    ]


def departure_busstop_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('departure_busstop', 'lähtopaikka')
    ]


def binding_registration_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova')
    ]
