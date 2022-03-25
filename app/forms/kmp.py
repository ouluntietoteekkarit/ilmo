from __future__ import annotations
from __future__ import annotations
from datetime import datetime
from typing import List

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_departure_location, make_attribute_phone_number, \
    make_attribute_email, make_attribute_lastname, make_attribute_firstname, \
    make_attribute_binding_registration_consent, make_attribute_name_consent, make_attribute_privacy_consent
from app.form_lib.form_controller import FormController, Event
from app.form_lib.lib import Quota, BaseParticipant
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()
        phone_number = recipient.get_phone_number()
        departure_location = recipient.get_departure_location()
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


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


_form_name = make_form_name(__file__)

_DEPARTURE_BUS_STOP_UNI = 'Yliopisto'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Merikoskenkatu (tuiran bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Linja-autoasema'


_DepartureLocationEnum = choices_to_enum(_form_name, 'departure_location', _get_departure_stops())

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    make_attribute_phone_number(),
    make_attribute_departure_location(_DepartureLocationEnum)
]

binding_consent_label = 'Ymmärrän, että ilmoittautuminen on sitova ja sitoudun maksamaan 40 euron (ei sisällä sitsien hintaa) maksun killalle *'

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_binding_registration_consent(binding_consent_label),
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('OTiT KMP', datetime(2021, 11, 19, 13, 37, 37),
               datetime(2021, 12, 3, 2, 00, 00), [Quota.default_quota(15, 15)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, False, _form_name, _event, _types)
