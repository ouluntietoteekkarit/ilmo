from __future__ import annotations

from abc import ABC
from typing import List, Tuple, Iterable, Type, Union, Callable, Any, Dict

from app import db
from .lib import BaseParticipant, BaseOtherAttributes, BaseModel, BaseAttachableAttribute, BaseFormComponent, \
    BaseTypeBuilder, AttributeFactory, TypeFactory, ATTRIBUTE_NAME_FIRSTNAME, ATTRIBUTE_NAME_LASTNAME, \
    ATTRIBUTE_NAME_EMAIL, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, \
    ATTRIBUTE_NAME_OTHER_ATTRIBUTES, ATTRIBUTE_NAME_PRIVACY_CONSENT, ATTRIBUTE_NAME_NAME_CONSENT, \
    BaseAttribute, ObjectAttribute, ListAttribute, DatetimeAttribute, \
    BoolAttribute, StringAttribute, IntAttribute, ATTRIBUTE_NAME_PHONE_NUMBER, \
    ATTRIBUTE_NAME_DEPARTURE_LOCATION, ATTRIBUTE_NAME_QUOTA, ATTRIBUTE_NAME_BINDING_REGISTRATION_CONSENT, \
    EnumAttribute

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


class ModelAttributesModel(db.Model, BaseOtherAttributes):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class BasicModel(db.Model, BaseModel):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class DbTypeFactory(TypeFactory):
    def __init__(self, required_participant_attributes: Iterable[BaseAttribute],
                 optional_participant_attributes: Iterable[BaseAttribute],
                 other_attributes: Iterable[BaseAttribute],
                 form_name: str):
        super().__init__(required_participant_attributes, optional_participant_attributes, other_attributes)
        self._form_name = form_name

    def make_type(self):
        factory = _DbAttributeFactory()
        required_participant: Type[BasicParticipantModel] = _ParticipantModelBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._required_participant_attributes)
        ).build()
        optional_participant: Type[BasicParticipantModel] = _ParticipantModelBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._optional_participant_attributes)
        ).build()
        other_attributes: Type[ModelAttributesModel] = _ModelAttributesBuilder(self._form_name).add_fields(
            self._parameters_to_fields(factory, self._other_attributes)
        ).build()
        return _ModelBuilder(self._form_name).add_fields([
            make_column_required_participants(required_participant),
            make_column_optional_participants(optional_participant),
            make_column_form_attributes(other_attributes)
        ]).build()


class _DbAttributeFactory(AttributeFactory):

    def _params_to_args(self, params: BaseAttribute) -> Tuple[str, Union[Callable[[Any], Any], None]]:
        return (
            params.get_attribute(),
            self._make_getter(params)
        )

    def _make_getter(self, params: BaseAttribute) -> Callable[[], Any]:
        # MEMO: May be possible to eliminate this method
        attribute = params.get_attribute()

        def getter(self) -> Any:
            return getattr(self, attribute)

        getter.__name__ = "get_{}".format(attribute)
        return getter

    def make_int_attribute(self, params: IntAttribute) -> BaseAttachableAttribute:
        return _AttachableIntColumn(*self._params_to_args(params))

    def make_string_attribute(self, params: StringAttribute) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if length is missing
        length = params.get_extra()['length']
        return _AttachableStringColumn(*self._params_to_args(params), length)

    def make_bool_attribute(self, params: BoolAttribute) -> BaseAttachableAttribute:
        return _AttachableBoolColumn(*self._params_to_args(params))

    def make_datetime_attribute(self, params: DatetimeAttribute) -> BaseAttachableAttribute:
        return _AttachableDatetimeColumn(*self._params_to_args(params))

    def make_enum_attribute(self, params: EnumAttribute) -> BaseAttachableAttribute:
        return _AttachableStringColumn(*self._params_to_args(params))

    def make_list_attribute(self, params: ListAttribute) -> BaseAttachableAttribute:
        list_type = params.get_list_type()
        return _AttachableRelationshipColumn(*self._params_to_args(params), list_type)

    def make_object_attribute(self, params: ObjectAttribute) -> BaseAttachableAttribute:
        model_type = params.get_object_type()
        return _AttachableRelationshipColumn(*self._params_to_args(params), model_type)


class _BaseDbBuilder(BaseTypeBuilder, ABC):
    def __init__(self, form_name: str):
        self._form_name = form_name


class _ModelBuilder(_BaseDbBuilder):

    def build(self, base_type: Type[db.Model] = None) -> Type[db.Model]:
        if not base_type:
            class TmpModel(BasicModel):
                __tablename__ = self._form_name

            base_type = TmpModel

        required = {
            ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS: hasattr(base_type, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS)
        }
        return self._do_build(base_type, required)


class _ParticipantModelBuilder(_BaseDbBuilder):

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


class _ModelAttributesBuilder(_BaseDbBuilder):

    def build(self, base_type: Type[db.Model] = None) -> Type[db.Model]:
        if not base_type:
            class TmpModel(ModelAttributesModel):
                __tablename__ = self._form_name + "_attributes"

            base_type = TmpModel

        required = {
            ATTRIBUTE_NAME_PRIVACY_CONSENT: hasattr(base_type, ATTRIBUTE_NAME_PRIVACY_CONSENT)
        }
        return self._do_build(base_type, required)


class _AttachableColumn(BaseAttachableAttribute, ABC):
    def __init__(self, *args, **kwargs):
        super(_AttachableColumn, self).__init__(*args, **kwargs)


class _AttachableStringColumn(_AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], length: int):
        super().__init__(attribute_name, getter)
        self._length = length

    def _make_field_value(self) -> Any:
        return db.Column(db.String(self._length))


class _AttachableIntColumn(_AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.Integer)


class _AttachableBoolColumn(_AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.Boolean())


class _AttachableDatetimeColumn(_AttachableColumn):

    def _make_field_value(self) -> Any:
        return db.Column(db.DateTime())


class _AttachableEnumColumn(_AttachableColumn):

    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None], enum_type: Type[Enum]):
        super().__init__(attribute_name, getter)
        self._enum_type = enum_type

    def _make_field_value(self) -> Any:
        return db.Column(db.Enum(self._enum_type))


class _AttachableRelationshipColumn(_AttachableColumn):

    def __init__(self,
                 attribute_name: str,
                 getter: Union[Callable[[Any], Any], None],
                 model_class: Union[Type[BaseFormComponent], Type[db.Model]]):
        super().__init__(attribute_name, getter)
        self._model_class = model_class

    def _make_field_value(self) -> Any:
        return db.Column(db.relationship(self._model_class.__name__))


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
