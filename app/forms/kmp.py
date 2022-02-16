from datetime import datetime
from typing import List, Iterable, Tuple

from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import PhoneNumberField, DepartureBusstopField, ShowNameConsentField, \
    BindingRegistrationConsentField, BasicForm
from .forms_util.models import BasicModel, DepartureBusstopColumn, PhoneNumberColumn, basic_model_csv_map, \
    phone_number_csv_map, departure_busstop_csv_map, binding_registration_csv_map
from .forms_util.models import BindingRegistrationConsentColumn

_form_name = file_path_to_form_name(__file__)

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


@BindingRegistrationConsentField(
    'Ymmärrän, että ilmoittautuminen on sitova ja sitoudun maksamaan 40 euron (ei sisällä sitsien hintaa) maksun killalle *')
@ShowNameConsentField()
@DepartureBusstopField(_get_choise(_get_departure_stops()))
@PhoneNumberField()
class _Form(BasicForm):
    pass


class _Model(BasicModel, DepartureBusstopColumn, PhoneNumberColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


class _Controller(FormController):

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
                "\nOlet ilmoittautunut OTiTin KMP:lle. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email,
                "\nPuhelinnumero: ", phone_number,
                "\nLähtöpaikka: ", departure_location,
                "\nKMP:llä Lappeenrannassa järjestettäville sitseille voit ilmoittautua osoitteessa https://forms.gle/aLLSsT1PpUQMQaNb8",
                "\n\nMaksuohjeet: ",
                "\nHinta: 40 euroa",
                "\nTilinumero: FI03 4744 3020 0116 87",
                "\nVastaanottajan nimi: Oulun Tietoteekkarit ry",
                "\nViestiksi \"KMP + etunimi ja sukunimi\"",
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])


# MEMO: (attribute, header_text)
_data_table_info = DataTableInfo(basic_model_csv_map() +
                                 phone_number_csv_map() +
                                 departure_busstop_csv_map() +
                                 binding_registration_csv_map())
_event = Event('OTiT KMP', datetime(2021, 11, 19, 13, 37, 37),
               datetime(2021, 12, 3, 2, 00, 00), 15, 15, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
