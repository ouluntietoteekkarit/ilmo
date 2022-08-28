from datetime import datetime
from typing import List, Union

from wtforms.validators import InputRequired

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_allergies, make_attribute_quota, make_attribute_name_consent, make_attribute_privacy_consent
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_wine, \
    make_attribute_usual_sitsi_liquor, make_enum_usual_sitsi_drink, make_enum_usual_sitsi_liquor, \
    make_enum_usual_sitsi_wine
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.lib import BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices
from app.form_lib.models import RegistrationModel


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_QUOTA_FUKSI = 'Fuksi'
_QUOTA_PRO = 'Pro'


class OtherQuota(Quota):
    def __init__(self, fuksiQuota: Quota, name: str, quota: int, reserve_quota: int = 0,
                 registration_start: Union[datetime, None] = None,
                 registration_end: Union[datetime, None] = None):
        super(OtherQuota, self).__init__(name, quota, reserve_quota, registration_start, registration_end)

        self._fuksiQuota = fuksiQuota

    def get_max_quota(self) -> int:
        return self._fuksiQuota.get_max_quota() - self._fuksiQuota.()


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        if recipient.get_quota() in [_QUOTA_FUKSI, _QUOTA_PRO]:
            return ' '.join([
                make_greet_line(recipient),
                """Olet ilmoittautunut OTiTin fuksisitseille. Sitsien pukukoodi on cocktail.

Älä vastaa tähän sähköpostiin, vastaus ei mene mihinkään."""
            ])

        return ' '.join([
            make_greet_line(recipient),
            """Olet ilmoittautunut OTiTin fuksisitseille. Sitsien pukukoodi on cocktail.
Tässä vielä maksuohjeet: 
Sitsien hinta on 20€. Maksu tapahtuu tilisiirrolla Oulun Tietoteekkarit ry:n tilille FI03 4744 3020 0116 87.
Kirjoita viestikenttään nimesi + fuksisitsit. Jos tulee kysyttävää, niin voit olla sähköpostitse yhteydessä 
pepeministeri@otit.fi

Älä vastaa tähän sähköpostiin, vastaus ei mene mihinkään."""
        ])


_form_name = make_form_name(__file__)


def _get_quotas(registration_start: datetime, registration_end: datetime) -> List[Quota]:
    fuksi_quota = Quota(_QUOTA_FUKSI, 100,  0,  registration_start,             datetime(2022, 9, 2, 23, 59, 59))
    return [
        fuksi_quota,
        Quota(_QUOTA_PRO,   8,    0,  registration_start,             registration_end),
        Quota('Hallitus',   11,   0,  registration_start,             registration_end),
        OtherQuota(fuksi_quota, 'Muu',        0,    0,  datetime(2022, 9, 3, 0, 0, 0),  registration_end)
    ]


_registration_start = datetime(2022, 8, 25, 12, 0, 0)
_registration_end = datetime(2022, 9, 4, 23, 59, 59)
_quotas = _get_quotas(_registration_start, _registration_end)

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_quotas))
_DrinkEnum = make_enum_usual_sitsi_drink(_form_name)
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_sitsi_wine(_form_name)

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies()
]
optional_participant_attributes = []
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('Fuksisitsit', _registration_start, _registration_end, _quotas, _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)
