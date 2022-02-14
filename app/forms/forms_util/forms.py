from typing import List, Tuple, Iterable

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import InputRequired, Optional, DataRequired, length, Email


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


def get_str_choices(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


def basic_form():
    if not hasattr(basic_form, 'type'):
        # MEMO: Must have same attribute names as BasicModel
        class BasicForm(FlaskForm):
            firstname = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
            lastname = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
            email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
            privacy_consent = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *', validators=[DataRequired()])

            def get_firstname(self) -> str:
                return self.firstname.data

            def get_lastname(self) -> str:
                return self.lastname.data

            def get_email(self) -> str:
                return self.email.data

            def get_privacy_consent(self) -> bool:
                return self.privacy_consent.data

        basic_form.type = BasicForm

    return basic_form.type


def show_name_consent_field(name_consent_txt: str = 'Sallin nimeni julkaisemisen osallistujalistassa tällä sivulla'):
    if not hasattr(show_name_consent_field, 'type'):
        # MEMO: Must have same attribute name as the correspoding one in BasicModel
        class ShowNameConsentField:
            show_name_consent = BooleanField(name_consent_txt)

        show_name_consent_field.type = ShowNameConsentField

    return show_name_consent_field.type


# MEMO: Must have same attribute names as PhoneNumberColumn
class PhoneNumberField:
    phone_number = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])


def departure_busstop_field(choices: List[Tuple[str, str]]):
    """
    MEMO: Choices of departure_busstop must be set dynamically.
          See https://wtforms.readthedocs.io/en/3.0.x/fields/#wtforms.fields.SelectField
    """
    if not hasattr(departure_busstop_field, 'type'):
        # MEMO: Must have same attribute names as DepartureBusstopColumn
        class DepartureBusstopField:
            departure_busstop = SelectField('Kilta *', choices=choices, validators=[DataRequired()])

        departure_busstop_field.type = DepartureBusstopField

    return departure_busstop_field.type


def guild_field(choices: List[Tuple[str, str]]):
    if not hasattr(guild_field, 'type'):
        # MEMO: Must have same attribute names as GuildColumn
        class GuildField:
            guild_name = SelectField('Kilta *', choices=choices, validators=[DataRequired()])

        guild_field.type = GuildField

    return guild_field.type


def binding_registration_consent_field(txt: str = 'Ymmärrän, että ilmoittautuminen on sitova *'):
    if not hasattr(binding_registration_consent_field, 'type'):
        # MEMO: Must have same attribute names as BindingRegistrationConsentColumn
        class BindingRegistrationConsentField:
            binding_registration_consent = BooleanField(txt, validators=[DataRequired()])

        binding_registration_consent_field.type = BindingRegistrationConsentField

    return binding_registration_consent_field.type
