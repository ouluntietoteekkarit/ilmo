from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import List, Tuple, Iterable, Type, Union, Any, Callable

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, FormField, Form, FieldList, Field, RadioField, IntegerField, \
    DateTimeField
from wtforms.validators import InputRequired, Optional

from app.form_lib.guilds import Guild
from app.form_lib.lib import BaseAttachableAttribute, BaseModel, BaseOtherAttributes, \
    BaseParticipant, BaseTypeBuilder, ATTRIBUTE_NAME_FIRSTNAME, ATTRIBUTE_NAME_LASTNAME, \
    ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, ATTRIBUTE_NAME_PRIVACY_CONSENT, AttributeFactory, \
    ObjectAttribute, IntAttribute, ListAttribute, DatetimeAttribute, BoolAttribute, \
    StringAttribute, BaseAttribute, TypeFactory, BaseFormComponent, EnumAttribute, attributes_to_fields, \
    ATTRIBUTE_NAME_OTHER_ATTRIBUTES, ATTRIBUTE_NAME_NAME_CONSENT, Quota
from app.form_lib.common_attributes import make_attribute_required_participants, make_attribute_optional_participants, \
    make_attribute_form_attributes


class BasicParticipantForm(Form, BaseParticipant):
    pass


class FormAttributesForm(Form, BaseOtherAttributes):
    asks_name_consent = False


class BasicForm(FlaskForm, BaseModel):
    pass


class BaseFormBuilder(BaseTypeBuilder, ABC):
    pass


class _FormBuilder(BaseFormBuilder):
    def __init__(self, asks_name_consent: bool):
        super().__init__()
        self._asks_name_consent = asks_name_consent

    def build(self, base_type: Type[BasicForm] = None) -> Type[BasicForm]:
        if not base_type:
            base_type = type('Form', (BasicForm,), {})

        required = self._get_required_attributes_for_base_model(base_type)
        form_type = self._do_build(base_type, required)
        form_type.asks_name_consent = self._asks_name_consent
        return form_type


class _ParticipantFormBuilder(BaseFormBuilder):
    def __init__(self, participant_type: str):
        super().__init__()
        self._participant_type = participant_type

    def build(self, base_type: Type[BasicParticipantForm] = None) -> Type[BasicParticipantForm]:
        if not base_type:
            name = "{}_ParticipantForm".format(self._participant_type)
            base_type = type(name, (BasicParticipantForm,), {})

        if self._participant_type == 'required':
            required = self._get_required_attributes_for_required_participant(base_type)
        else:
            required = self._get_required_attributes_for_optional_participant(base_type)

        return self._do_build(base_type, required)


class _OtherAttributesBuilder(BaseFormBuilder):

    def build(self, base_type: Type[FormAttributesForm] = None) -> Type[FormAttributesForm]:
        if not base_type:
            base_type = type('AttributesForm', (FormAttributesForm,), {})

        required = self._get_required_attributes_for_other_attributes(base_type)
        return self._do_build(base_type, required)


class RequiredIf(InputRequired):
    """Validator which makes a field required if another field is set and has a truthy value.
    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
        - https://www.reddit.com/r/flask/comments/7y1k6p/af_wtforms_required_if_validator/
    """

    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None):
        super().__init__(message)
        self.other_field_name = other_field_name

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class RequiredIfValue(InputRequired):
    """Validator which makes a field required if another field is set and has a truthy value.
    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
        - https://www.reddit.com/r/flask/comments/7y1k6p/af_wtforms_required_if_validator/
    """

    field_flags = ('requiredif',)

    def __init__(self, other_field_name, value, message=None):
        super().__init__(message)
        self.other_field_name = other_field_name
        self.value = value

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        value = self.value
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data == value):
            super(RequiredIfValue, self).__call__(form, field)
        else:
            Optional().__call__(form, field)


class MergeFormField(FormField):
    """
    Encapsulate a form as a field in another form.
    Overrides populate_obj to produce flat objects
    instead of maintaining the form's object hierarchy.
    No attribute name mangling takes place.
    """

    def populate_obj(self, obj, name):
        tmp = type('', (object,), dict())()
        self.form.populate_obj(tmp)
        for attr in vars(tmp):
            setattr(obj, attr, getattr(tmp, attr))


class FlatFormField(FormField):
    """
    Encapsulate a form as a field in another form.
    Overrides populate_obj to produce flat objects
    instead of maintaining the form's object hierarchy.
    The attribute names of the enclosed form are
    prefixed with this field's name and an underscore.
    """

    def populate_obj(self, obj, name):
        tmp = type('', (object,), dict())()
        self.form.populate_obj(tmp)
        for attr in vars(tmp):
            setattr(obj, self.name + '_' + attr, getattr(tmp, attr))


class _AttachableField(BaseAttachableAttribute, ABC):
    def __init__(self, attribute_name: str, label: str, validators: Iterable, getter: Union[Callable[[Any], Any], None]):
        super().__init__(attribute_name, getter)
        self._label = label
        self._validators = validators


class _AttachableIntField(_AttachableField):

    def _make_field_value(self) -> Any:
        return IntegerField(self._label, validators=self._validators)


class _AttachableStringField(_AttachableField):

    def _make_field_value(self) -> Any:
        return StringField(self._label, validators=self._validators)


class _AttachableBoolField(_AttachableField):

    def _make_field_value(self) -> Any:
        return BooleanField(self._label, validators=self._validators)


class _AttachableDatetimeField(_AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 format: str):
        super().__init__(attribute, label, validators, getter)
        self._format = format

    def _make_field_value(self) -> Any:
        return DateTimeField(self._label, validators=self._validators, format=self._format)


class _AttachableEnumField(_AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 enum_type: Type[Enum]):
        super().__init__(attribute, label, validators, getter)
        self._enum_type = enum_type

    def _make_choices(self, enum_type: Type[Enum]):
        choices = []
        for name in enum_type.__members__:
            choices.append((name, name))

        return choices

    def _make_field_value(self) -> Any:
        choices = self._make_choices(self._enum_type)
        length = len(choices)
        if length == 0:
            raise Exception("Empty enumeration is not allowed.")
        elif length > 4:
            return SelectField(self._label, choices=choices, validators=self._validators)
        else:
            return RadioField(self._label, choices=choices, validators=self._validators)


class _AttachableFieldListField(_AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 field: Union[BaseFormComponent, Field],
                 count: int):
        super().__init__(attribute, label, validators, getter)
        self._field = field
        self._min_entries = count
        self._max_entries = count

    def _make_field_value(self) -> Any:
        return FieldList(self._field, min_entries=self._min_entries, max_entries=self._max_entries)


class _AttachableFormField(_AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 form_type: Type[FormAttributesForm]):
        super().__init__(attribute, label, validators, getter)
        self._form_type = form_type

    def _make_field_value(self) -> Any:
        return FormField(self._form_type)


class FormTypeFactory(TypeFactory):

    def _determine_asks_name_consent(self) -> bool:
        for attribute in self._other_attributes:
            if attribute.get_attribute() == ATTRIBUTE_NAME_NAME_CONSENT:
                return True

        return False

    def make_type(self):
        factory = _FormAttributeFactory()
        form_attributes = []

        if len(self._required_participant_attributes) > 0:
            fields = attributes_to_fields(factory, self._required_participant_attributes)
            required_participant: Type[BasicParticipantForm] = _ParticipantFormBuilder('required').add_fields(fields).build()
            tmp = make_attribute_required_participants(required_participant, self._required_participant_count)
            form_attributes.append(tmp)

        if self._optional_participant_count > 0 and len(self._optional_participant_attributes) > 0:
            fields = attributes_to_fields(factory, self._optional_participant_attributes)
            optional_participant: Type[BasicParticipantForm] = _ParticipantFormBuilder('optional').add_fields(fields).build()
            tmp = make_attribute_optional_participants(optional_participant, self._optional_participant_count)
            form_attributes.append(tmp)

        if len(self._other_attributes) > 0:
            fields = attributes_to_fields(factory, self._other_attributes)
            other_attributes: Type[FormAttributesForm] = _OtherAttributesBuilder().add_fields(fields).build()
            tmp = make_attribute_form_attributes(other_attributes)
            form_attributes.append(tmp)

        asks_name_consent = self._determine_asks_name_consent()
        return _FormBuilder(asks_name_consent).add_fields(attributes_to_fields(factory, form_attributes)).build()


class _FormAttributeFactory(AttributeFactory):

    def _get_validators(self, params: BaseAttribute):
        return params.try_get_extra('validators', [])

    def _params_to_args(self, params: BaseAttribute) -> Tuple[str, str, Iterable, Union[Callable[[Any], Any], None]]:
        return (
            params.get_attribute(),
            params.get_label(),
            self._get_validators(params),
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
        return _AttachableIntField(*self._params_to_args(params))

    def make_string_attribute(self, params: StringAttribute) -> BaseAttachableAttribute:
        return _AttachableStringField(*self._params_to_args(params))

    def make_bool_attribute(self, params: BoolAttribute) -> BaseAttachableAttribute:
        return _AttachableBoolField(*self._params_to_args(params))

    def make_datetime_attribute(self, params: DatetimeAttribute) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if format is missing
        datetime_format = params.get_datetime_format()
        return _AttachableDatetimeField(*self._params_to_args(params), datetime_format)

    def make_enum_attribute(self, params: EnumAttribute) -> BaseAttachableAttribute:
        enum_type = params.get_enum_type()
        return _AttachableEnumField(*self._params_to_args(params), enum_type)

    def make_list_attribute(self, params: ListAttribute) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if field is missing
        list_type = params.get_list_type()
        count = params.get_count()
        return _AttachableFieldListField(*self._params_to_args(params), FormField(list_type), count)

    def make_object_attribute(self, params: ObjectAttribute) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if form_type is missing
        form_type = params.get_object_type()
        return _AttachableFormField(*self._params_to_args(params), form_type)


def choices_to_enum(form_name: str, enum_name: str, values: Iterable[str]) -> Type[Enum]:
    # TODO: Test with and without name
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
