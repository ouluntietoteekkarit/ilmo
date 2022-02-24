from __future__ import annotations

from abc import ABC
from typing import List, Tuple, Iterable, Type, Union, Any, Callable

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, FormField, Form, FieldList, Field, RadioField, IntegerField, \
    DateTimeField
from wtforms.validators import InputRequired, Optional, DataRequired, length, Email

from app.forms.forms_util.form_controller import Quota
from app.forms.forms_util.guilds import Guild
from app.forms.forms_util.lib import BaseAttachableAttribute, BaseModel, BaseAttributes, \
    BaseParticipant, BaseTypeBuilder, ATTRIBUTE_NAME_FIRSTNAME, ATTRIBUTE_NAME_LASTNAME, ATTRIBUTE_NAME_EMAIL, \
    ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, ATTRIBUTE_NAME_OTHER_ATTRIBUTES, \
    ATTRIBUTE_NAME_PRIVACY_CONSENT, ATTRIBUTE_NAME_NAME_CONSENT, AttributeFactory, ObjectAttributeParameters, \
    IntAttributeParameters, ListAttributeParameters, DatetimeAttributeParameters, BoolAttributeParameters, \
    StringAttributeParameters, BaseAttributeParameters, TypeFactory


class BasicParticipantForm(Form, BaseParticipant):
    pass


class FormAttributesForm(Form, BaseAttributes):
    asks_name_consent = False


# MEMO: Must have same attribute names as BasicModel
class BasicForm(FlaskForm, BaseModel):
    pass


class BaseFormBuilder(BaseTypeBuilder, ABC):
    pass


class FormBuilder(BaseFormBuilder):

    def build(self, base_type: Type[BasicForm] = None) -> Type[BasicForm]:
        if not base_type:
            class TmpForm(BasicForm):
                pass

            base_type = TmpForm

        required = {
            ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS: hasattr(base_type, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS)
        }
        return self._do_build(base_type, required)


class ParticipantFormBuilder(BaseFormBuilder):

    def build(self, base_type: Type[BasicParticipantForm] = None) -> Type[BasicParticipantForm]:
        if not base_type:
            class TmpForm(BasicParticipantForm):
                pass

            base_type = TmpForm

        required = {
            ATTRIBUTE_NAME_FIRSTNAME: hasattr(base_type, ATTRIBUTE_NAME_FIRSTNAME),
            ATTRIBUTE_NAME_LASTNAME: hasattr(base_type, ATTRIBUTE_NAME_LASTNAME)
        }
        return self._do_build(base_type, required)


class FormAttributesBuilder(BaseFormBuilder):

    def build(self, base_type: Type[FormAttributesForm] = None) -> Type[FormAttributesForm]:
        if not base_type:
            class TmpForm(FormAttributesForm):
                pass

            base_type = TmpForm

        required = {
            ATTRIBUTE_NAME_PRIVACY_CONSENT: hasattr(base_type, ATTRIBUTE_NAME_PRIVACY_CONSENT)
        }
        return self._do_build(base_type, required)


class RequiredIf(InputRequired):
    """Validator which makes a field required if another field is set and has a truthy value.
    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
        - https://www.reddit.com/r/flask/comments/7y1k6p/af_wtforms_required_if_validator/
    """

    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

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

    def __init__(self, other_field_name, value, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message
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

    :param form_class:
        A subclass of Form that will be encapsulated.
    :param separator:
        A string which will be suffixed to this field's name to create the
        prefix to enclosed fields. The default is fine for most uses.
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

    :param form_class:
        A subclass of Form that will be encapsulated.
    :param separator:
        A string which will be suffixed to this field's name to create the
        prefix to enclosed fields. The default is fine for most uses.
    """

    def populate_obj(self, obj, name):
        tmp = type('', (object,), dict())()
        self.form.populate_obj(tmp)
        for attr in vars(tmp):
            setattr(obj, self.name + '_' + attr, getattr(tmp, attr))


class AttachableField(BaseAttachableAttribute, ABC):
    def __init__(self, attribute_name: str, label: str, validators: Iterable, getter: Union[Callable[[Any], Any], None]):
        self._attribute_name = attribute_name
        self._label = label
        self._validators = validators
        self._getter = getter


class AttachableIntField(AttachableField):

    def _make_field_value(self) -> Any:
        return IntegerField(self._label, validators=self._validators)


class AttachableStringField(AttachableField):

    def _make_field_value(self) -> Any:
        return StringField(self._label, validators=self._validators)


class AttachableBoolField(AttachableField):

    def _make_field_value(self) -> Any:
        return BooleanField(self._label, validators=self._validators)


class AttachableDatetimeField(AttachableField):
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


class AttachableSelectField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 choices: List[Tuple[str, str]]):
        super().__init__(attribute, label, validators, getter)
        self._choice = choices

    def _make_field_value(self) -> Any:
        return SelectField(self._label, choices=self._choice, validators=self._validators)


class AttachableRadioField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 choices: List[Tuple[str, str]]):
        super().__init__(attribute, label, validators, getter)
        self._choices = choices

    def _make_field_value(self) -> Any:
        return RadioField(self._label, choices=self._choices, validators=self._validators)


class AttachableFieldListField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 field: Field,
                 min_entries: int,
                 max_entries: int):
        super().__init__(attribute, label, validators, getter)
        self.field = field
        self._min_entries = min_entries
        self._max_entries = max_entries

    def _make_field_value(self) -> Any:
        return FieldList(self.field, min_entries=self._min_entries, max_entries=self._max_entries)


class AttachableFormField(AttachableField):
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

    def make_type(self):
        factory = FormAttributeFactory()
        required_participant: Type[BasicParticipantForm] = ParticipantFormBuilder().add_fields(
            self._parameters_to_fields(factory, self._required_participant_attributes)
        ).build()
        optional_participant: Type[BasicParticipantForm] = ParticipantFormBuilder().add_fields(
            self._parameters_to_fields(factory, self._optional_participant_attributes)
        ).build()
        other_attributes: Type[FormAttributesForm] = FormAttributesBuilder().add_fields(
            self._parameters_to_fields(factory, self._other_attributes)
        ).build()
        return FormBuilder().add_fields([
            make_field_required_participants(required_participant, 1),
            make_field_optional_participants(optional_participant, 1),
            make_field_form_attributes(other_attributes)
        ]).build()


class FormAttributeFactory(AttributeFactory):

    def _get_validators(self, params: BaseAttributeParameters):
        return params.try_get_extra('validators', [])

    def _params_to_args(self, params: BaseAttributeParameters) -> Tuple[str, str, Iterable, Union[Callable[[Any], Any], None]]:
        return (
            params.get_attribute(),
            params.get_label(),
            self._get_validators(params),
            params.get_getter()
        )

    def make_int_attribute(self, params: IntAttributeParameters) -> BaseAttachableAttribute:
        return AttachableIntField(*self._params_to_args(params))

    def make_string_attribute(self, params: StringAttributeParameters) -> BaseAttachableAttribute:
        return AttachableStringField(*self._params_to_args(params))

    def make_bool_attribute(self, params: BoolAttributeParameters) -> BaseAttachableAttribute:
        return AttachableBoolField(*self._params_to_args(params))

    def make_datetime_attribute(self, params: DatetimeAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if format is missing
        date_format = params.get_extra()['format']
        return AttachableDatetimeField(*self._params_to_args(params), date_format)

    def make_list_attribute(self, params: ListAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if field is missing
        field = params.get_extra()['field']
        min_entries = params.try_get_extra('min_entries', 0)
        max_entries = params.try_get_extra('max_entries', 0)
        return AttachableFieldListField(*self._params_to_args(), field, min_entries, max_entries)

    def make_object_attribute(self, params: ObjectAttributeParameters) -> BaseAttachableAttribute:
        # MEMO: Ensures crash if form_type is missing
        form_type = params.get_extra()['form_type']
        return AttachableFormField(*self._params_to_args(), form_type)


def make_field_firstname(extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as FirstnameColumn
    def get_firstname(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_FIRSTNAME).data

    return AttachableStringField(ATTRIBUTE_NAME_FIRSTNAME, 'Etunimi *', [length(max=50)] + list(extra_validators), get_firstname)


def make_field_lastname(extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as LastnameColumn
    def get_lastname(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_LASTNAME).data

    return AttachableStringField(ATTRIBUTE_NAME_LASTNAME, 'Sukunimi *', [length(max=50)] + list(extra_validators), get_lastname)


def make_field_email(extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as EmailColumn
    def get_email(self) -> str:
        return getattr(self, ATTRIBUTE_NAME_EMAIL).data

    return AttachableStringField(ATTRIBUTE_NAME_EMAIL, 'Sähköposti *', [Email(), length(max=100)] + list(extra_validators), get_email)


def make_field_phone_number(extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as PhoneNumberColumn
    def get_phone_number(self) -> str:
        return self.phone_number.data

    return AttachableStringField('phone_number', 'Puhelinnumero *', [length(max=20)] + list(extra_validators), get_phone_number)


def make_field_departure_location(choices: List[Tuple[str, str]], extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as DepartureBusstopColumn
    def get_departure_location(self) -> str:
        return self.departure_location.data

    return AttachableSelectField('departure_location', 'Lähtöpaikka *', [length(max=50)] + list(extra_validators), get_departure_location, choices)


def make_field_quota(label: str, choices: List[Tuple[str, str]], extra_validators: Iterable = []) -> AttachableField:
    # MEMO: Must have same attribute names as QuotaColumn
    def get_quota(self) -> str:
        return self.quota.data

    return AttachableSelectField('quota', label, [length(max=50)] + list(extra_validators), get_quota, choices)


def make_field_name_consent(txt: str = 'Sallin nimeni julkaisemisen osallistujalistassa tällä sivulla') -> AttachableField:
    # MEMO: Must have same attribute name as the correspoding one in BasicModel
    def get_name_consent(self) -> bool:
        return getattr(self, ATTRIBUTE_NAME_NAME_CONSENT).data

    # MEMO: Come up with a solution to this.
    # form.asks_name_consent = True

    return AttachableBoolField(ATTRIBUTE_NAME_NAME_CONSENT, txt, [], get_name_consent)


def make_field_binding_registration_consent(txt: str = 'Ymmärrän, että ilmoittautuminen on sitova *') -> AttachableField:
    # MEMO: Must have same attribute names as BindingRegistrationConsentColumn
    return AttachableBoolField('binding_registration_consent', txt, [DataRequired()], None)


def make_field_privacy_consent(txt: str = 'Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *'):
    # MEMO: Must have same attribute names as model type
    return AttachableBoolField(ATTRIBUTE_NAME_PRIVACY_CONSENT, txt, [DataRequired()], None)


def make_field_required_participants(form_type: Type[BasicParticipantForm], count: int = 1) -> AttachableField:
    def get_required_participants(self) -> Union[Iterable[BasicParticipantForm], FieldList]:
        return self.required_participants

    return AttachableFieldListField(ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, '', [DataRequired], get_required_participants, FormField(form_type), count, count)


def make_field_optional_participants(form_type: Type[BasicParticipantForm], count: int = 0) -> AttachableField:
    def get_optional_participants(self) -> Union[Iterable[BasicParticipantForm], FieldList]:
        return self.optional_participants

    return AttachableFieldListField(ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, '', [], get_optional_participants, FormField(form_type), count, count)


def make_field_form_attributes(form_type: Type[FormAttributesForm]) -> AttachableField:
    def get_other_attributes(self) -> FormAttributesForm:
        return self.form_attributes.data

    return AttachableFormField(ATTRIBUTE_NAME_OTHER_ATTRIBUTES, '', [], get_other_attributes, form_type)


def make_default_form() -> Type[BasicForm]:
    _Participant = make_default_participant_form()
    return FormBuilder().add_fields([
        make_field_required_participants(_Participant),
        make_field_privacy_consent()
    ]).build()


def make_default_participant_form() -> Type[BasicParticipantForm]:
    return ParticipantFormBuilder().add_fields([
        make_field_firstname([InputRequired()]),
        make_field_lastname([InputRequired()]),
        make_field_email([InputRequired()])
    ]).build()


def make_default_form_attributes_form() -> Type[FormAttributesForm]:
    return FormAttributesBuilder().add_fields([
        make_field_privacy_consent()
    ]).build()


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
