from datetime import datetime
from typing import List

from wtforms.validators import InputRequired

from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, DataTableInfo, Event, Quota
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import get_str_choices, FormBuilder, make_default_participant_form,\
    make_field_required_participants, make_field_departure_location, make_field_phone_number, make_field_name_consent,\
    make_field_binding_registration_consent, make_field_privacy_consent, ParticipantFormBuilder
from .forms_util.models import BasicModel, basic_model_csv_map, \
    phone_number_csv_map, departure_busstop_csv_map, binding_registration_csv_map

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


_Participant = ParticipantFormBuilder().add_fields([
    make_field_phone_number([InputRequired()]),
    make_field_departure_location(get_str_choices(_get_departure_stops()), [InputRequired()])
]).build(make_default_participant_form())

_Form = FormBuilder().add_fields([
    make_field_required_participants(_Participant, 1),
    make_field_name_consent(),
    make_field_binding_registration_consent('Ymmärrän, että ilmoittautuminen on sitova ja sitoudun maksamaan 40 euron (ei sisällä sitsien hintaa) maksun killalle *'),
    make_field_privacy_consent()
]).build()


class _Model(BasicModel): #, DepartureBusstopColumn, PhoneNumberColumn, BindingRegistrationConsentColumn):
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
               datetime(2021, 12, 3, 2, 00, 00), [Quota.default_quota(15, 15)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
