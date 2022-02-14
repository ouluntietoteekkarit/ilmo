from wtforms import StringField, RadioField, SelectField
from wtforms.validators import DataRequired, length
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.forms import RequiredIf, basic_form, show_name_consent_field, get_str_choices
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.models import BasicModel

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
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


_name_consent_type = show_name_consent_field()
class _Form(basic_form(), _name_consent_type):
    alkoholi = RadioField('Alkoholillinen/Alkoholiton *', choices=get_str_choices(_get_drinks()), validators=[DataRequired()])
    mieto = SelectField('Mieto juoma *', choices=get_str_choices(_get_alcoholic_drinks()), validators=[RequiredIf(other_field_name='alkoholi', value=_DRINK_ALCOHOLIC)])
    pitsa = SelectField('Pitsa *', choices=get_str_choices(_get_pizzas()), validators=[DataRequired()])
    allergiat = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])


class _Model(BasicModel):
    __tablename__ = _form_name
    alkoholi = db.Column(db.String(32))
    mieto = db.Column(db.String(32))
    pitsa = db.Column(db.String(32))
    allergiat = db.Column(db.String(256))


_event = Event('OTiT Pitsakaljasitsit ilmoittautuminen', datetime(2021, 10, 26, 12, 00, 00), datetime(2021, 11, 9, 23, 59, 59), 60, 30, issubclass(_Form, _name_consent_type))


class _Controller(FormController):

    def __init__(self):
        super().__init__(_event, _Form, _Model, get_module_info(), _get_data_table_info())

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool):
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Olet varasijalla. ",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Pitsakalja sitseille. Tässä vielä maksuohjeet: ",
                "\n\n", "Hinta alkoholillisen juoman kanssa on 20€ ja alkoholittoman juoman ",
                "kanssa 17€. Maksu tapahtuu tilisiirrolla Oulun Tietoteekkarit ry:n tilille ",
                "FI03 4744 3020 0116 87. Kirjoita viestikenttään nimesi, ",
                "Pitsakalja-sitsit sekä alkoholiton tai alkoholillinen valintasi mukaan.",
                "\n\nJos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä pepeministeri@otit.fi",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo([
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('email', 'email'),
        ('alkoholi', 'alkoholi'),
        ('mieto', 'mieto'),
        ('pitsa', 'pitsa'),
        ('allergiat', 'allergia'),
        ('show_name_consent', 'hyväksyn nimeni julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ])
