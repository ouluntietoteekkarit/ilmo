from wtforms import SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from typing import Any, List, Iterable, Tuple

from app import db
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.forms import basic_form, PhoneNumberField, departure_busstop_field, show_name_consent_field
from .forms_util.models import BasicModel, PhoneNumberColumn, DepartureBusstopColumn

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

    def post_request_handler(self, request) -> Any:
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    # MEMO: "Evil" Covariant parameter
    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.firstname.data
        lastname = form.lastname.data
        for entry in entries:
            if entry.firstname == firstname and entry.lastname == lastname:
                return True
        return False

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: _Form, reserve: bool) -> str:
        firstname = str(form.firstname.data)
        lastname = str(form.lastname.data)
        email = str(form.email.data)
        phone_number = str(form.phone_number.data)
        departure_location = str(form.lahtopaikka.data)
        quota = str(form.kiintio.data)
        if reserve:
            return ' '.join([
                "\"Hei", firstname, " ", lastname,
                "\n\nOlet ilmoittautunut OTiTin Fuksicursiolle. Olet varasijalla. ",
                "Jos fuculle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""
            ])
        else:
            return ' '.join([
                "\"Hei", firstname, " ", lastname,
                "\n\nOlet ilmoittautunut OTiTin Fuksicursiolle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location, "\nKiintiö: ", quota,
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään.\""
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
