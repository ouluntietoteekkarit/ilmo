from __future__ import annotations

from abc import ABC
from typing import List, Tuple, Iterable, Type, Union, Callable, Any, Dict

from app import db


# MEMO: Must have same attribute names as BasicForm
from .lib import BaseParticipant, BaseAttributes, BaseModel, BaseAttachableAttribute, BaseFormComponent, \
    BaseTypeBuilder, AttributeFactory, TypeFactory, ATTRIBUTE_NAME_FIRSTNAME, ATTRIBUTE_NAME_LASTNAME, \
    ATTRIBUTE_NAME_EMAIL, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, \
    ATTRIBUTE_NAME_OTHER_ATTRIBUTES, ATTRIBUTE_NAME_PRIVACY_CONSENT, ATTRIBUTE_NAME_NAME_CONSENT, \
    BaseAttributeParameters, ObjectAttributeParameters, ListAttributeParameters, DatetimeAttributeParameters, \
    BoolAttributeParameters, StringAttributeParameters, IntAttributeParameters, ATTRIBUTE_NAME_PHONE_NUMBER, \
    ATTRIBUTE_NAME_DEPARTURE_LOCATION

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


class BasicParticipantModel(db.Model, BaseParticipant):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class ModelAttributesModel(db.Model, BaseAttributes):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class BasicModel(db.Model, BaseModel):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class DbTypeFactory(TypeFactory):
    def __init__(self, required_participant_attributes: Iterable[BaseAttributeParameters],
                 optional_participant_attributes: Iterable[BaseAttributeParameters],
                 other_attributes: Iterable[BaseAttributeParameters],
                 form_name: str):
        super().__init__(required_participant_attributes, optional_participant_attributes, other_attributes)
        self._form_name = form_name

    def make_type(self):
        factory = DbAttributeFactory()
        required_participant: Type[BasicParticipantModel] = ParticipantModelBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._required_participant_attributes)
        ).build()
        optional_participant: Type[BasicParticipantModel] = ParticipantModelBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._optional_participant_attributes)
        ).build()
        other_attributes: Type[ModelAttributesModel] = ModelAttributesBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._other_attributes)
        ).build()
        return ModelBuilder(self._form_name).add_fields([
            make_column_required_participants(required_participant),
            make_column_optional_participants(optional_participant),
            make_column_form_attributes(other_attributes)
        ]).build()


class DbAttributeFactory(AttributeFactory):

    def _params_to_args(self, params: BaseAttributeParameters) -> Tuple[str, Union[Callable[[Any], Any], None]]:
        return (
            params.get_attribute(),
            params.get_getter()
        )

    def make_int_attribute(self, params: IntAttributeParameters) -> BaseAttachableAttribute:
        return AttachableIntColumn(*self._params_to_args(params))

    def make_string_attribute(self, params: StringAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if length is missing
        length = params.get_extra()['length']
        return AttachableStringColumn(*self._params_to_args(params), length)

    def make_bool_attribute(self, params: BoolAttributeParameters) -> BaseAttachableAttribute:
        return AttachableBoolColumn(*self._params_to_args(params))

    def make_datetime_attribute(self, params: DatetimeAttributeParameters) -> BaseAttachableAttribute:
        return AttachableDatetimeColumn(*self._params_to_args(params))

    def make_list_attribute(self, params: ListAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if model_class is missing
        model_type = params.get_extra()['model_class']
        return AttachableRelationshipColumn(*self._params_to_args(params))

    def make_object_attribute(self, params: ObjectAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if model_class is missing
        model_type = params.get_extra()['model_class']
        return AttachableRelationshipColumn(*self._params_to_args(params))


class BaseDbBuilder(BaseTypeBuilder, ABC):
    def __init__(self, form_name: str):
        self._form_name = form_name


class ModelBuilder(BaseDbBuilder):

    def build(self, base_type: Type[db.Model] = None) -> Type[db.Model]:
        if not base_type:
            class TmpModel(BasicModel):
                __tablename__ = self._form_name

            base_type = TmpModel

        required = {
            ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS: hasattr(base_type, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS)
        }
        return self._do_build(base_type, required)


class ParticipantModelBuilder(BaseDbBuilder):

    def build(self, base_type: Type[db.Model] = None) -> Type[db.Model]:
        if not base_type:
            class TmpModel(BasicParticipantModel):
                __tablename__ = self._form_name + "_participant"

            base_type = TmpModel

        required = {
            ATTRIBUTE_NAME_FIRSTNAME: hasattr(base_type, ATTRIBUTE_NAME_FIRSTNAME),
            ATTRIBUTE_NAME_LASTNAME: hasattr(base_type, ATTRIBUTE_NAME_LASTNAME)
        }
        return self._do_build(base_type, required)


class ModelAttributesBuilder(BaseDbBuilder):

    def build(self, base_type: Type[db.Model] = None) -> Type[db.Model]:
        if not base_type:
            class TmpModel(ModelAttributesModel):
                __tablename__ = self._form_name + "_attributes"

            base_type = TmpModel

        required = {
            ATTRIBUTE_NAME_PRIVACY_CONSENT: hasattr(base_type, ATTRIBUTE_NAME_PRIVACY_CONSENT)
        }
        return self._do_build(base_type, required)


class AttachableColumn(BaseAttachableAttribute, ABC):
    def __init__(self, *args, **kwargs):
        super(AttachableColumn, self).__init__(*args, **kwargs)


class AttachableStringColumn(AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], length: int):
        super().__init__(attribute_name, getter)
        self._length = length

    def _make_field_value(self) -> Any:
        return db.Column(db.String(self._length))


class AttachableIntColumn(AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.Integer)


class AttachableBoolColumn(AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.Boolean())


class AttachableDatetimeColumn(AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.DateTime())


class AttachableRelationshipColumn(AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], model_class: Type[db.Model]):
        super().__init__(attribute_name, getter)
        self._model_class = model_class

    def _make_field_value(self) -> Any:
        return db.Column(db.relationship(self._model_class.__name__))


def make_column_firstname() -> AttachableColumn:
    def get_firstname(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_FIRSTNAME)

    return AttachableStringColumn(ATTRIBUTE_NAME_FIRSTNAME, get_firstname, 50)


def make_column_lastname() -> AttachableColumn:
    def get_lastname(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_LASTNAME)

    return AttachableStringColumn(ATTRIBUTE_NAME_LASTNAME, get_lastname, 50)


def make_column_email() -> AttachableColumn:
    def get_email(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_EMAIL)

    return AttachableStringColumn(ATTRIBUTE_NAME_EMAIL, get_email, 100)


def make_column_phone_number() -> AttachableColumn:
    def get_phone_number(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_PHONE_NUMBER)

    return AttachableStringColumn(ATTRIBUTE_NAME_PHONE_NUMBER, get_phone_number, 20)


def make_column_departure_location() -> AttachableColumn:
    def get_departure_location(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_DEPARTURE_LOCATION)

    return AttachableStringColumn(ATTRIBUTE_NAME_DEPARTURE_LOCATION, get_departure_location, 50)


def make_column_quota() -> AttachableColumn:
    def get_quota(self) -> str:
        return getattr(self, 'quota')

    return AttachableStringColumn('quota', get_quota, 50)


def make_column_name_consent() -> AttachableColumn:
    def get_name_consent(self) -> bool:
        return getattr(self, ATTRIBUTE_NAME_NAME_CONSENT)

    return AttachableBoolColumn(ATTRIBUTE_NAME_NAME_CONSENT, get_name_consent)


def make_column_binding_registration_consent() -> AttachableColumn:
    return AttachableBoolColumn('binding_registration_consent', None)


def make_column_privacy_consent() -> AttachableColumn:
    return AttachableBoolColumn(ATTRIBUTE_NAME_PRIVACY_CONSENT, None)


def make_column_required_participants(model_type: Type[BasicParticipantModel]) -> AttachableColumn:
    # TODO: Add typing
    def get_required_participants(self):
        return getattr(self, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS)

    return AttachableRelationshipColumn(ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, get_required_participants, model_type)


def make_column_optional_participants(model_type: Type[BasicParticipantModel]) -> AttachableColumn:
    # TODO: Add typing
    def get_optional_participants(self):
        return getattr(self, ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS)

    return AttachableRelationshipColumn(ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, get_optional_participants, model_type)


def make_column_form_attributes(model_type: Type[ModelAttributesModel]) -> AttachableColumn:
    def get_other_attributes(self) -> ModelAttributesModel:
        return getattr(self, ATTRIBUTE_NAME_OTHER_ATTRIBUTES)

    return AttachableRelationshipColumn(ATTRIBUTE_NAME_OTHER_ATTRIBUTES, get_other_attributes, model_type)


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


def departure_location_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('departure_location', 'lähtopaikka')
    ]


def binding_registration_csv_map() -> List[Tuple[str, str]]:
    # MEMO: (attribute, header_text)
    return [
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova')
    ]
