from datetime import datetime
from typing import List, Iterable, Tuple

from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.forms import PhoneNumberField, DepartureBusstopField, ShowNameConsentField, \
    BindingRegistrationConsentField, BasicForm
from .forms_util.models import BasicModel, DepartureBusstopColumn, PhoneNumberColumn
from .forms_util.models import BindingRegistrationConsentColumn

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
    return _form_module
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_choise(values: Iterable[str]) -> List[Tuple[str, str]]:
    choices = []
    for val in values:
        choices.append((val, val))
    return choices


@BindingRegistrationConsentField('Ymmärrän, että ilmoittautuminen on sitova ja sitoudun maksamaan 40 euron (ei sisällä sitsien hintaa) maksun killalle *')
@ShowNameConsentField()
@DepartureBusstopField(_get_choise(_get_departure_stops()))
@PhoneNumberField()
class _Form(BasicForm):
    pass


class _Model(BasicModel, DepartureBusstopColumn, PhoneNumberColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


_event = Event('OTiT KMP ilmoittautuminen', datetime(2021, 11, 19, 13, 37, 37), datetime(2021, 12, 3, 2, 00, 00),
               15, 15, _Form.asks_name_consent)


class _Controller(FormController):

    def __init__(self):
        super().__init__(_event, _Form, _Model, get_module_info(), _get_data_table_info())

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email_address()
        phone_number = model.get_phone_number()
        departure_location = model.get_departure_busstop()
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin KMP:lle. Olet varasijalla. ",
                "Jos KMPlle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OTiTin KMPlle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email, "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location,
                "\nKMP:llä Lappeenrannassa järjestettäville sitseille voit ilmoittautua osoitteessa https://forms.gle/aLLSsT1PpUQMQaNb8",
                "\n\nMaksuohjeet: ",
                "\nHinta: 40 euroa",
                "\nTilinumero: FI03 4744 3020 0116 87",
                "\nVastaanottajan nimi: Oulun Tietoteekkarit ry",
                "\nViestiksi \"KMP + etunimi ja sukunimi\"",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo([
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('email', 'email'),
        ('phone_number', 'puhelinnumero'),
        ('departure_busstop', 'lahtopaikka'),
        ('show_name_consent', 'hyväksyn nimeni julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('binding_registration_consent', 'ymmärrän, että ilmoittautuminen on sitova'),
        ('datetime', 'datetime')
    ])
