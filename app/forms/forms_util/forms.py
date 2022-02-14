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


# MEMO: Must have same attribute names as BasicModel
class BasicForm(FlaskForm):
    firstname = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    lastname = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    privacy_consent = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
    asks_name_consent = False

    def get_firstname(self) -> str:
        return self.firstname.data

    def get_lastname(self) -> str:
        return self.lastname.data

    def get_email(self) -> str:
        return self.email.data

    def get_privacy_consent(self) -> bool:
        return self.privacy_consent.data

    def get_participant_count(self) -> int:
        """
        Returns the number of participants this form covers.
        Overriding this method allows handling group registrations.
        """
        return 1


class ShowNameConsentField:
    def __init__(self, txt: str = 'Sallin nimeni julkaisemisen osallistujalistassa tällä sivulla'):
        self._txt = txt

    def __call__(self, form: BasicForm):
        # MEMO: Must have same attribute name as the correspoding one in BasicModel
        form.show_name_consent = BooleanField(self._txt)
        form.asks_name_consent = True
        return form


class PhoneNumberField:
    def __init__(self):
        pass

    def __call__(self, form: BasicForm):
        # MEMO: Must have same attribute names as PhoneNumberColumn
        form.phone_number = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
        return form


class DepartureBusstopField:
    def __init__(self, choices: List[Tuple[str, str]]):
        self._choices = choices

    def __call__(self, form: BasicForm):
        # MEMO: Must have same attribute names as DepartureBusstopColumn
        form.departure_busstop = SelectField('Lähtöpaikka *', choices=self._choices, validators=[DataRequired()])
        return form


class GuildField:
    def __init__(self, choices: List[Tuple[str, str]]):
        self._choices = choices

    def __call__(self, form: BasicForm):
        # MEMO: Must have same attribute names as GuildColumn
        form.guild_name = SelectField('Kilta *', choices=self._choices, validators=[DataRequired()])
        return form


class BindingRegistrationConsentField:
    def __init__(self, txt: str = 'Ymmärrän, että ilmoittautuminen on sitova *'):
        self._txt = txt

    def __call__(self, form: BasicForm):
        # MEMO: Must have same attribute names as BindingRegistrationConsentColumn
        form.binding_registration_consent = BooleanField(self._txt, validators=[DataRequired()])
        return form
