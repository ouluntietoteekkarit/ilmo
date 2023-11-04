from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Iterable, Type

from wtforms.validators import InputRequired

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_lastname, make_attribute_firstname, make_attribute_email, \
    make_attribute_quota, make_attribute_privacy_consent, make_attribute_name_consent, make_attribute_allergies
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_liquor, \
    make_attribute_usual_humanisti_sitsi_wine, get_usual_humanisti_sitsi_wines, get_usual_sitsi_liquors, get_usual_sitsi_drinks, \
    make_enum_usual_sitsi_drink, make_enum_usual_sitsi_liquor, make_enum_usual_humanisti_sitsi_wine
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import StringAttribute, EnumAttribute, BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.guilds import GUILD_OTIT, GUILD_SIK, GUILD_VERBA
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut OPMx3 sitseille. Olet varasijalla.",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä soteministeri@otit.fi."
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                """\nOlet ilmoittautunut OPMx3 sitseille. Sitsit järjestetään teekkaritalolla 19.11.2023 klo 18.00 alkaen."

Tässä vielä maksuohjeet:
Maksettava summa on 16€. 32€ jos osallistut avecin kanssa. Maksu tapahtuu tilisiirrolla
Oulun Tietoteekkarit ry:n tilille FI03 4744 3020 0116 87. Kirjoita viestikenttään oma nimesi, avecisi
nimi ja \"OPMx3 sitsit\". Maksun eräpäivä on 19.11.2023.

Sitsien jatkoja varten mukaan OPMx2.

Jos tulee kysyttävää, voit olla sähköpostitse yhteydessä soteministeri@otit.fi.
Älä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."""
            ])


_form_name = make_form_name(__file__)

_registration_start = datetime(2023, 11, 5, 12, 0, 0)
_registration_end = datetime(2023, 11, 12, 23, 59, 59)

def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_VERBA, 22, 50, _registration_start, _registration_end),
        Quota(GUILD_OTIT, 22, 50, _registration_start, _registration_end),
        Quota(GUILD_SIK, 22, 50, _registration_start, _registration_end),
    ]


def _make_attribute_seating_preference(validators: Iterable = None):
    return StringAttribute('seating_preference', 'Pyötäseuratoive', 'Pyötäseuratoive', 100, validators=validators)

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_DrinkEnum = make_enum_usual_sitsi_drink(_form_name)
_LiquorEnum = make_enum_usual_sitsi_liquor(_form_name)
_WineEnum = make_enum_usual_humanisti_sitsi_wine(_form_name)


participant_attributes = [
    make_attribute_firstname(validators=[InputRequired()]),
    make_attribute_lastname(validators=[InputRequired()]),
    make_attribute_email(validators=[InputRequired()]),
] + [
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_drink(_DrinkEnum, validators=[InputRequired()]),
    make_attribute_usual_sitsi_liquor(_LiquorEnum, validators=[InputRequired()]),
    make_attribute_usual_humanisti_sitsi_wine(_WineEnum, validators=[InputRequired()]),
    make_attribute_allergies(),
    _make_attribute_seating_preference()
]

optional_participant_attributes = participant_attributes

other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()])
]
_types = make_types(participant_attributes, optional_participant_attributes, other_attributes, 1, 1, _form_name)

_event = Event('OPMx3 sitsit', _registration_start, _registration_end, _get_quotas(), _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)


