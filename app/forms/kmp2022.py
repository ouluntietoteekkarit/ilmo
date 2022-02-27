from datetime import datetime
from enum import Enum
from typing import List, Dict, Collection, Iterable, Type

from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.form_controller import FormController, DataTableInfo, Event, Quota
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.guilds import GUILD_SIK, GUILD_OTIT
from app.form_lib.models import basic_model_csv_map, departure_location_csv_map
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_departure_location, make_attribute_name_consent, make_attribute_privacy_consent
from app.form_lib.lib import StringAttribute, EnumAttribute
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices

_form_name = file_path_to_form_name(__file__)

_QUOTA_WITH_ACCOMODATION = GUILD_OTIT + ' (majoituksella)'
_QUOTA_WITHOUT_ACCOMICATION = GUILD_SIK + ' (ei majoitusta)'


_DEPARTURE_BUS_STOP_UNI = 'Yliopisto (X-oven edestä)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkadun bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Keskusta (Linja-autoasema)'


_ROOM_COMPOSITION_SAME_SEX = 'Samaa sukupuolta'
_ROOM_COMPOSITION_NO_PREFERENCE = 'Ei väliä'


def _get_sexes() -> List[str]:
    return [
        'Mies',
        'Nainen',
        'Muu'
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(_QUOTA_WITH_ACCOMODATION, 42, 15),
        Quota(_QUOTA_WITHOUT_ACCOMICATION, 13, 5)
    ]


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_room_sex_options() -> List[str]:
    return [
        _ROOM_COMPOSITION_SAME_SEX,
        _ROOM_COMPOSITION_NO_PREFERENCE
    ]


def _make_attribute_roommate_preference(validators: Iterable = None):
    return StringAttribute('roommate_preference', 'Huonekaveri toiveet (max 2)', 'Huonekaveri toiveet', 100, validators=validators)


def _make_attribute_room_sex_composition(sex_composition_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('room_sex_composition', 'Haluatko majoittua samaa sukupuolta olevien kanssa?', 'huonekaverien sukupuoli', sex_composition_enum, validators=validators)


def _make_attribute_sex(sex_enum: Type[Enum], validators: Iterable = None):
    return EnumAttribute('sex', 'Sukupuoli', 'Sukupuoli', sex_enum, validators=validators)


def _make_attribute_allergies(validators: Iterable = None):
    return StringAttribute('allergies', 'Erityisruokavaliot/allergiat', 'Erityisruokavaliot', 200, validators=validators)


_DepartureEnum = choices_to_enum(_form_name, 'departure', _get_departure_stops())
_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_SexCompositionEnum = choices_to_enum(_form_name, 'sex_compositin', _get_room_sex_options())
_SexEnum = choices_to_enum(_form_name, 'sex', _get_sexes())

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    make_attribute_departure_location(_DepartureEnum),
    make_attribute_quota(_QuotaEnum),
    _make_attribute_roommate_preference(),
    _make_attribute_room_sex_composition(_SexCompositionEnum),
    _make_attribute_sex(_SexEnum),
    _make_attribute_allergies()
]

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent()
]

types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)
_Form = types.get_form_type()
_Model = types.get_model_type()


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        if reserve:
            return """{}Olet ilmoittautunut OTiTin ja SIKin KMP:lle. Olet varasijalla. Jos KMP:lle jää jostain syystä vapaita
paikkoja, sinuun voidaan olla yhteydessä.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))
        else:
            return """{}Ole ilmoittautunut OTiTin ja SIKin KMP:lle. KMP järjestetään 18. - 20.3. Tampereella.

Tässä vielä maksuohjeet:
OTiT-laisille summa on 60€. SIKkiläisille summa 35€. Osallistumismaksu maksetaan tilille 
FI03 4744 3020 0116 87. Maksun saajan nimi: Oulun Tietoteekkarit ry. Viestiksi KMP + oma nimi.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))


_data_table_info = DataTableInfo(
    basic_model_csv_map() +
    departure_location_csv_map() +
    [('quota', 'kiintiö'),
     ('roommate_preference', 'huonekaveri toiveet'),
     ('room_sex_composition', 'huonekaverien sukupuoli'),
     ('sex', 'sukupuoli'),
     ('allergies', 'erikoisruokavaliot')]
)
_event = Event('OTiT KMP', datetime(2021, 2, 25, 13, 37, 00),
               datetime(2022, 3, 10, 0, 0, 0), _get_quotas(), _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
