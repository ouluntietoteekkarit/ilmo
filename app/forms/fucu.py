from wtforms import SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from typing import List, Iterable, Tuple

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.forms import basic_form, PhoneNumberField, departure_busstop_field, show_name_consent_field
from .forms_util.models import BasicModel, PhoneNumberColumn, DepartureBusstopColumn

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """
    Returns a singleton object containing this form's module information.
    """
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
    return _form_module

# P U B L I C   M O D U L E   I N T E R F A C E   E N D


_PARTICIPANT_FUKSI = 'Fuksi'
_PARTICIPANT_PRO = 'Pro'
_PARTICIPANT_BOARD_MEMBER = 'Hallitus'
_PARTICIPANT_OTHER = 'Muu'

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_participants() -> List[str]:
    return [
        _PARTICIPANT_FUKSI,
        _PARTICIPANT_PRO,
        _PARTICIPANT_BOARD_MEMBER,
        _PARTICIPANT_OTHER
    ]


def _get_choise(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


class _Form(basic_form(),
            PhoneNumberField,
            departure_busstop_field(_get_choise(_get_departure_stops())),
            show_name_consent_field()):
    kiintio = SelectField('Kiintiö *', choices=_get_choise(_get_participants()), validators=[DataRequired()])


class _Model(BasicModel, PhoneNumberColumn, DepartureBusstopColumn):
    __tablename__ = _form_name
    kiintio = db.Column(db.String(32))


class _Controller(FormController):

    def __init__(self):
        event = Event('OTiT Fuksicursio ilmoittautuminen', datetime(2021, 10, 29, 12, 00, 00), datetime(2024, 11, 4, 21, 00, 00), 5, 20)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = model.get_email()
        phone_number = model.get_phone_number()
        departure_location = model.get_departure_busstop()
        quota = model.kiintio
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Olet varasijalla.",
                "Jos fuculle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin Fuksicursiolle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, " ", lastname,
                "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location, "\nKiintiö: ", quota,
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('email', 'email'),
        ('phone_number', 'puhelinnumero'),
        ('departure_busstop', 'lahtopaikka'),
        ('kiintio', 'kiintio'),
        ('show_name_consent', 'hyväksyn nimeni julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
