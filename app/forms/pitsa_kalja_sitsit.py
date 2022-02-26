from wtforms import StringField, RadioField, SelectField
from wtforms.validators import DataRequired, length
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.forms import RequiredIf, get_str_choices, FormBuilder, make_default_participant_form,\
    make_field_required_participants, make_field_name_consent, make_field_privacy_consent
from app.form_lib.form_controller import FormController, DataTableInfo, Event
from app.form_lib.lib import Quota
from app.form_lib.models import BasicModel, basic_model_csv_map

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


_Participant = make_default_participant_form()
_Form = FormBuilder().add_fields([
    make_field_required_participants(_Participant, 1),
    make_field_name_consent(),
    make_field_privacy_consent()
]).build()
_Form.alkoholi = RadioField('Alkoholillinen/Alkoholiton *', choices=get_str_choices(_get_drinks()), validators=[DataRequired()])
_Form.mieto = SelectField('Mieto juoma *', choices=get_str_choices(_get_alcoholic_drinks()), validators=[RequiredIf(other_field_name='alkoholi', value=_DRINK_ALCOHOLIC)])
_Form.pitsa = SelectField('Pitsa *', choices=get_str_choices(_get_pizzas()), validators=[DataRequired()])
_Form.allergiat = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])


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
                "\n\n Hinta alkoholillisen juoman kanssa on 20€ ja alkoholittoman juoman ",
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
_event = Event('OTiTin Pitsakaljasitsit', datetime(2021, 10, 26, 12, 00, 00),
               datetime(2021, 11, 9, 23, 59, 59), [Quota.default_quota(60, 30)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
