from __future__ import annotations

from abc import ABC
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Iterable, Type, Union, Callable, Any, Dict, Collection, TypeVar

from app import db
from .lib import BaseParticipant, BaseOtherAttributes, BaseRegistration, BaseAttachableAttribute, BaseFormComponent, \
    BaseTypeBuilder, AttributeFactory, TypeFactory, BaseAttribute, ObjectAttribute, \
    ListAttribute, DatetimeAttribute, BoolAttribute, StringAttribute, IntAttribute, EnumAttribute, \
    attributes_to_fields, ATTRIBUTE_NAME_OTHER_ATTRIBUTES, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, \
    ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS
from .common_attributes import make_attribute_required_participants, make_attribute_optional_participants, \
    make_attribute_other_attributes


class BasicParticipantModel(BaseParticipant, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class OtherAttributesModel(BaseOtherAttributes, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)


class RegistrationModel(BaseRegistration, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer(), primary_key=True)
    create_time = db.Column(db.DateTime())


class DbTypeFactory(TypeFactory):
    def __init__(self,
                 required_participant_attributes: Collection[BaseAttribute],
                 optional_participant_attributes: Collection[BaseAttribute],
                 other_attributes: Collection[BaseAttribute],
                 required_participant_count: int,
                 optional_participant_count: int,
                 form_name: str):
        super().__init__(required_participant_attributes,
                         optional_participant_attributes,
                         other_attributes,
                         required_participant_count,
                         optional_participant_count)
        self._form_name = form_name

    def _establish_relationships(self, parent: db.Model, child_tables: Iterable[db.Model]) -> None:
        parent_id_column = "{}.id".format(parent.__tablename__)
        for table in child_tables:
            table.parent_id = db.Column(db.Integer, db.ForeignKey(parent_id_column))

    def make_type(self) -> Tuple[Type[RegistrationModel], Callable[[int, int, datetime], RegistrationModel]]:

        def factory_method(required_participant_count: int,
                           optional_participant_count: int,
                           time: datetime) -> RegistrationModel:
            obj = model_type(create_time=time)

            if required_participant_type is not None:
                setattr(obj, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS,
                        [required_participant_type() for i in range(0, required_participant_count)])

            if optional_participant_type is not None:
                setattr(obj, ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS,
                        [optional_participant_type() for i in range(0, optional_participant_count)])

            setattr(obj, ATTRIBUTE_NAME_OTHER_ATTRIBUTES,
                    other_attributes_type() if other_attributes_type is not None else None)

            return obj

        factory = _DbAttributeFactory()
        form_attributes = []
        required_participant_type = None
        optional_participant_type = None
        other_attributes_type = None

        if len(self._required_participant_attributes) > 0:
            required_participant_type: Union[Type[BasicParticipantModel], None] = (
                _ParticipantBuilder(self._form_name, 'required')
                .add_fields(attributes_to_fields(factory, self._required_participant_attributes))
                .build())
            form_attributes.append(make_attribute_required_participants(required_participant_type))

        if self._optional_participant_count > 0 and len(self._optional_participant_attributes) > 0:
            optional_participant_type: Union[Type[BasicParticipantModel], None] = (
                _ParticipantBuilder(self._form_name, 'optional')
                .add_fields(attributes_to_fields(factory, self._optional_participant_attributes))
                .build())
            form_attributes.append(make_attribute_optional_participants(optional_participant_type))

        if len(self._other_attributes) > 0:
            other_attributes_type: Union[Type[OtherAttributesModel], None] = (
                _OtherAttributesBuilder(self._form_name)
                .add_fields(attributes_to_fields(factory, self._other_attributes))
                .build())
            tmp = make_attribute_other_attributes(other_attributes_type)
            form_attributes.append(tmp)

        model_type: Type[Union[RegistrationModel, db.Model]] = (
            _ModelBuilder(self._form_name)
            .add_fields(attributes_to_fields(factory, form_attributes))
            .build())

        model_types = filter(None, [
            required_participant_type,
            optional_participant_type,
            other_attributes_type
        ])
        self._establish_relationships(model_type, model_types)

        return model_type, factory_method


class _DbAttributeFactory(AttributeFactory):

    def _params_to_args(self, params: BaseAttribute) -> Tuple[str, Union[Callable[[Any], Any], None]]:
        return (
            params.get_attribute(),
            self._make_getter(params)
        )

    def _make_enum_getter(self, params: BaseAttribute) -> Callable[[], Any]:
        # MEMO: enum.value causes data handling bugs.
        # MEMO: enum.name may be incorrect
        attribute = params.get_attribute()

        def getter(self) -> Union[str, int]:
            return getattr(self, attribute).name

        return self._name_getter(getter, attribute)

    def make_int_attribute(self, params: IntAttribute) -> BaseAttachableAttribute:
        return _AttachableIntColumn(*self._params_to_args(params))

    def make_string_attribute(self, params: StringAttribute) -> BaseAttachableAttribute:
        length = params.get_length()
        return _AttachableStringColumn(*self._params_to_args(params), length)

    def make_bool_attribute(self, params: BoolAttribute) -> BaseAttachableAttribute:
        return _AttachableBoolColumn(*self._params_to_args(params))

    def make_datetime_attribute(self, params: DatetimeAttribute) -> BaseAttachableAttribute:
        return _AttachableDatetimeColumn(*self._params_to_args(params))

    def make_enum_attribute(self, params: EnumAttribute) -> BaseAttachableAttribute:
        return _AttachableEnumColumn(params.get_attribute(),
                                     self._make_enum_getter(params),
                                     params.get_enum_type())

    def make_list_attribute(self, params: ListAttribute) -> BaseAttachableAttribute:
        list_type = params.get_list_type()
        return _AttachableRelationshipColumn(*self._params_to_args(params), list_type, True)

    def make_object_attribute(self, params: ObjectAttribute) -> BaseAttachableAttribute:
        model_type = params.get_object_type()
        return _AttachableRelationshipColumn(*self._params_to_args(params), model_type, False)


class _BaseDbBuilder(BaseTypeBuilder, ABC):
    def __init__(self, form_name: str):
        super().__init__()
        self._form_name = form_name


class _ModelBuilder(_BaseDbBuilder):

    def build(self, base_type: Type[RegistrationModel] = None) -> Type[RegistrationModel]:
        if not base_type:
            name = self._form_name
            base_type = type(name, (RegistrationModel,), {'__tablename__': name})

        required = self._get_required_attributes_for_base_model(base_type)
        return self._do_build(base_type, required)


class _ParticipantBuilder(_BaseDbBuilder):
    def __init__(self, form_name: str, participant_type: str):
        super().__init__(form_name)
        assert participant_type in ['required', 'optional']
        self._participant_type = participant_type

    def build(self, base_type: Type[BasicParticipantModel] = None) -> Type[BasicParticipantModel]:
        if not base_type:
            name = "{}_{}_participant".format(self._form_name, self._participant_type)
            base_type = type(name, (BasicParticipantModel,), {'__tablename__': name})

        if self._participant_type == 'required':
            required = self._get_required_attributes_for_required_participant(base_type)
        else:
            required = self._get_required_attributes_for_optional_participant(base_type)

        return self._do_build(base_type, required)


class _OtherAttributesBuilder(_BaseDbBuilder):

    def build(self, base_type: Type[OtherAttributesModel] = None) -> Type[OtherAttributesModel]:
        if not base_type:
            name = self._form_name + "_attributes"
            base_type = type(name, (OtherAttributesModel,), {'__tablename__': name})

        required = self._get_required_attributes_for_other_attributes(base_type)
        return self._do_build(base_type, required)


class _AttachableColumn(BaseAttachableAttribute, ABC):
    def __init__(self, attribute_name: str, getter: Union[Callable[[Any], Any], None]):
        super().__init__(attribute_name, getter)


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

    def __init__(self, attribute_name: str,
                 getter: Union[Callable[[Any], Any], None],
                 enum_type: Type[Enum]):
        super().__init__(attribute_name, getter)
        self._enum_type = enum_type

    def _make_field_value(self) -> Any:
        return db.Column(db.Enum(self._enum_type))


class _AttachableRelationshipColumn(_AttachableColumn):

    def __init__(self,
                 attribute_name: str,
                 getter: Union[Callable[[Any], Any], None],
                 model_class: Union[Type[BaseFormComponent], Type[db.Model]],
                 use_list: bool):
        super().__init__(attribute_name, getter)
        self._model_class = model_class
        self._use_list = use_list

    def _make_field_value(self) -> Any:
        return db.relationship(self._model_class, uselist=self._use_list)
