from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any, List, Iterable, Tuple

from app import db
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.forms import RequiredIf
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

"""Singleton instance containing this form module's information."""
_form_module = None
_form_name = file_path_to_form_name(__file__)


def get_module_info() -> ModuleInfo:
    """
    Returns this form's module information.
    """
    global _form_module
    if _form_module is None:
        _form_module = ModuleInfo(_Controller, True, _form_name)
    return _form_module


# P U B L I C   M O D U L E   I N T E R F A C E   E N D


_DRINK_ALCOHOLIC = 'Alkoholillinen'
_DRINK_NON_ALCOHOLIC = 'Alkoholiton'

_DRINK_ALCOHOLIC_MILD_BEER = 'Olut'
_DRINK_ALCOHOLIC_MILD_CIDER = 'Siideri'

_PIZZA_MEAT = 'Liha'
_PIZZA_CHICKEN = 'Kana'
_PIZZA_VEGETARIAN = 'Vege'


def _get_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_alcoholic_drinks() -> List[str]:
    return [
        _DRINK_ALCOHOLIC_MILD_BEER,
        _DRINK_ALCOHOLIC_MILD_CIDER
    ]


def _get_pizzas() -> List[str]:
    return [
        _PIZZA_MEAT,
        _PIZZA_CHICKEN,
        _PIZZA_VEGETARIAN
    ]


def _get_choices(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    alkoholi = RadioField('Alkoholillinen/Alkoholiton *', choices=_get_choices(_get_drinks()), validators=[DataRequired()])
    mieto = SelectField('Mieto juoma *', choices=_get_choices(_get_alcoholic_drinks()), validators=[RequiredIf(other_field_name='alkoholi', value="Alkoholillinen")])
    pitsa = SelectField('Pitsa *', choices=_get_choices(_get_pizzas()), validators=[DataRequired()])
    allergiat = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])
    consent0 = BooleanField('Hyväksyn nimeni julkaisemisen tällä sivulla')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = _form_name
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    alkoholi = db.Column(db.String(32))
    mieto = db.Column(db.String(32))
    pitsa = db.Column(db.String(32))
    allergiat = db.Column(db.String(256))
    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())

    def get_firstname(self) -> str:
        return self.etunimi

    def get_lastname(self) -> str:
        return self.sukunimi

    def get_email(self) -> str:
        return self.email

    def get_show_name_consent(self) -> bool:
        return self.consent0


class _Controller(FormController):

    def __init__(self):
        event = Event('OTiT Pitsakaljasitsit ilmoittautuminen', datetime(2021, 10, 26, 12, 00, 00), datetime(2021, 11, 9, 23, 59, 59), 60, 30)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def post_request_handler(self, request) -> Any:
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    # MEMO: "Evil" Covariant parameter
    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                return True
        return False

    # MEMO: "Evil" Covariant parameter
    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, form: _Form, reserve: bool):
        firstname = str(form.etunimi.data)
        lastname = str(form.sukunimi.data)
        if reserve:
            return ' '.join([
                "\"Hei", firstname, " ", lastname,
                "\n\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Olet varasijalla. ",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\"",
            ])
        else:
            return ' '.join([
                "\"Hei", firstname, " ", lastname,
                "\n\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Tässä vielä maksuohjeet: ",
                "\n\n", "Hinta alkoholillisen juoman kanssa on 20€ ja alkoholittoman juoman ",
                "kanssa 17€. Maksu tapahtuu tilisiirrolla Oulun Tietoteekkarit ry:n tilille ",
                "FI03 4744 3020 0116 87. Kirjoita viestikenttään nimesi, ",
                "Pitsakalja-sitsit sekä alkoholiton tai alkoholillinen valintasi mukaan.",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""])

    # MEMO: "Evil" Covariant parameters
    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        return _Model(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            alkoholi=form.alkoholi.data,
            mieto=form.mieto.data,
            pitsa=form.pitsa.data,
            allergiat=form.allergiat.data,
            consent0=form.consent0.data,
            consent1=form.consent1.data,
            datetime=nowtime
        )


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('etunimi', 'etunimi'),
        ('sukunimi', 'sukunimi'),
        ('email', 'email'),
        ('alkoholi', 'alkoholi'),
        ('mieto', 'mieto'),
        ('pitsa', 'pitsa'),
        ('allergiat', 'allergia'),
        ('consent0', 'hyväksyn nimeni julkaisemisen'),
        ('consent1', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
