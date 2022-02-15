from wtforms import StringField, RadioField, SelectField
from wtforms.validators import DataRequired, length
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import RequiredIf, get_str_choices, BasicForm, ShowNameConsentField
from .forms_util.form_controller import FormController, DataTableInfo, Event
from .forms_util.models import BasicModel, basic_model_csv_map

_form_name = file_path_to_form_name(__file__)


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


@ShowNameConsentField()
class _Form(BasicForm):
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


class _Controller(FormController):

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


# MEMO: (attribute, header_text)
_data_table_info = DataTableInfo(basic_model_csv_map() + [
        ('alkoholi', 'alkoholi'),
        ('mieto', 'mieto'),
        ('pitsa', 'pitsa'),
        ('allergiat', 'allergia')])
_event = Event('OTiT Pitsakaljasitsit ilmoittautuminen', datetime(2021, 10, 26, 12, 00, 00),
               datetime(2021, 11, 9, 23, 59, 59), 60, 30, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
