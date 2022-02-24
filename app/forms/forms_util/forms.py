from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Iterable, Type, Union, Any, Callable

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, FormField, Form, FieldList, Field, RadioField
from wtforms.validators import InputRequired, Optional, DataRequired, length, Email

from app.forms.forms_util.form_controller import Quota
from app.forms.forms_util.guilds import Guild
from app.forms.forms_util.lib import BaseAttachable

ATTRIBUTE_NAME_FIRSTNAME = 'firstname'
ATTRIBUTE_NAME_LASTNAME = 'lastname'
ATTRIBUTE_NAME_EMAIL = 'email'
ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS = 'required_participants'
ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS = 'optional_participants'
ATTRIBUTE_NAME_OTHER_ATTRIBUTES = 'other_attributes'
ATTRIBUTE_NAME_PRIVACY_CONSENT = 'privacy_consent'
ATTRIBUTE_NAME_NAME_CONSENT = 'show_name_consent'


class BasicParticipantForm(Form):
    pass


class FormAttributesForm(Form):
    asks_name_consent = False


# MEMO: Must have same attribute names as BasicModel
class BasicForm(FlaskForm):
    pass


class BaseBuilder(ABC):
    def __init__(self):
        self._fields: List[AttachableField] = []

    def reset(self) -> BaseBuilder:
        self._fields = []
        return self

    def add_field(self, field: AttachableField) -> BaseBuilder:
        self._fields.append(field)
        return self

    def add_fields(self, fields: Iterable[AttachableField]) -> BaseBuilder:
        for field in fields:
            self.add_field(field)

        return self

    @abstractmethod
    def build(self, base_type: Type[Form] = None) -> Type[Form]:
        pass


class FormBuilder(BaseBuilder):

    def build(self, base_type: Type[BasicForm] = None) -> Type[BasicForm]:
        if not base_type:
            class TmpForm(BasicForm):
                pass

            base_type = TmpForm

        required = {
            'has_required_participants': hasattr(base_type, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS),
            'asks_name': hasattr(base_type, ATTRIBUTE_NAME_NAME_CONSENT),
        }

        for field in self._fields:
            field.attach_to(base_type)

            if field.get_attribute_name() in required:
                required[field.get_attribute_name()] = True

        for value in required.values():
            if not value:
                raise Exception(ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS + "is a mandatory attribute of " + BasicForm.__name__)

        base_type.asks_name_consent = asks_name

        return base_type


class ParticipantFormBuilder(BaseBuilder):

    def build(self, base_type: Type[BasicParticipantForm] = None) -> Type[BasicParticipantForm]:
        if not base_type:
            class TmpForm(BasicParticipantForm):
                pass

            base_type = TmpForm

        has_firstname = hasattr(base_type, ATTRIBUTE_NAME_FIRSTNAME)
        has_lastname = hasattr(base_type, ATTRIBUTE_NAME_LASTNAME)

        for field in self._fields:
            field.attach_to(base_type)
            has_firstname = has_firstname or field.get_attribute_name() == ATTRIBUTE_NAME_FIRSTNAME
            has_lastname = has_lastname or field.get_attribute_name() == ATTRIBUTE_NAME_LASTNAME

        if not has_firstname:
            raise Exception(ATTRIBUTE_NAME_FIRSTNAME + " is a mandatory attribute of " + BasicParticipantForm.__name__)

        if not has_lastname:
            raise Exception(ATTRIBUTE_NAME_LASTNAME + " is a mandatory attribute of " + BasicParticipantForm.__name__)

        return base_type


class FormAttributesBuilder(BaseBuilder):

    def build(self, base_type: Type[FormAttributesForm] = None) -> Type[FormAttributesForm]:
        if not base_type:
            class TmpForm(FormAttributesForm):
                pass

            base_type = TmpForm

        has_privacy_consent = hasattr(base_type, ATTRIBUTE_NAME_PRIVACY_CONSENT)

        for field in self._fields:
            field.attach_to(base_type)
            has_privacy_consent = has_privacy_consent or field.get_attribute_name() == ATTRIBUTE_NAME_PRIVACY_CONSENT

        if not has_privacy_consent:
            raise Exception("Privacy consent is a mandatory attribute of FormAttributesForm.")

        return base_type


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


class AttachableField(BaseAttachable):
    def __init__(self, attribute_name: str, label: str, validators: Iterable, getter: Union[Callable[[Any], Any], None]):
        self._attribute_name = attribute_name
        self._label = label
        self._validators = validators
        self._getter = getter

    def _attach(self, form: Type[Form], field: Field) -> Type[Form]:
        setattr(form, self._attribute_name, field)
        if self._getter:
            setattr(form, self._getter.__name__, self._getter)

        return form

    def get_attribute_name(self) -> str:
        return self._attribute_name

    @abstractmethod
    def attach_to(self, form: Type[Form]) -> Type[Form]:
        pass


class AttachableStringField(AttachableField):

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, StringField(self._label, validators=self._validators))


class AttachableBoolField(AttachableField):

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, BooleanField(self._label, validators=self._validators))


class AttachableSelectField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 choices: List[Tuple[str, str]]):
        super().__init__(attribute, label, validators, getter)
        self._choice = choices

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, SelectField(self._label, choices=self._choice, validators=self._validators))


class AttachableRadioField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 choices: List[Tuple[str, str]]):
        super().__init__(attribute, label, validators, getter)
        self._choices = choices

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, RadioField(self._label, choices=self._choices, validators=self._validators))


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

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, FieldList(self.field, min_entries=self._min_entries, max_entries=self._max_entries))


class AttachableFormField(AttachableField):
    def __init__(self,
                 attribute: str,
                 label: str,
                 validators: Iterable,
                 getter: Union[Callable[[Any], Any], None],
                 form_type: Type[FormAttributesForm]):
        super().__init__(attribute, label, validators, getter)
        self._form_type = form_type

    def attach_to(self, form: Type[Form]) -> Type[Form]:
        return self._attach(form, FormField(self._form_type))


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
