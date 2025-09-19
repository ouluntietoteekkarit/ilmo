from __future__ import annotations

from datetime import datetime
from typing import List

from wtforms.validators import InputRequired, Email, Length

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info


# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Vuosijuhlaviikon keilausilta"
_is_enabled = True
_start_date = datetime(2025, 9, 19, 12, 00, 00)
_end_date = datetime(2025, 9, 22, 23, 59, 59)


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()

        if reserve:
            result = ' '.join([
                make_greet_line(recipient),
                "Olet ilmoittautunut keilailemaan Alppila Bowlingiin 23.9. klo 17. Olet toistaiseksi varasijalla.\n",
                "Jos tapahtumaan järjestyy lisäratoja tai paikkoja vapautuu muuten, olemme sinuun yhteydessä.\n\n",
                "Jos tulee kysyttävää, voit olla yhteydessä sähköpostitse urheiluministeri(at)otit.fi tai Telegramissa @Susssy22.\n\n"
                "Tähän sähköpostiin ei voi vastata."
            ])
        else:
            result = ' '.join([
                make_greet_line(recipient),
                "Olet ilmoittautunut keilailemaan Alppila Bowlingiin 23.9. klo 17!\n\n",
                "Muistathan saapua keilahallille hyvissä ajoin ennen viittä.\n",
                "Jos et pääsekään paikalle, peruthan osallistumisesi mahdollisimman pian, jotta voimme tarjota paikkasi jonossa oleville.\n\n",
                "Jos tulee kysyttävää, voit olla yhteydessä sähköpostitse urheiluministeri(at)otit.fi tai Telegramissa @Susssy22.\n\n"
                "Tähän sähköpostiin ei voi vastata."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota('Osallistuja', 20, 100),
    ]


def hide_title():
    return True

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()])
]


other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event(_event_name,
               _start_date,
               _end_date,
               _get_quotas(),
               _types.asks_name_consent(),
               True)

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
