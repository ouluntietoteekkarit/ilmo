from __future__ import annotations

from datetime import datetime
from typing import List

from wtforms.validators import InputRequired, Email, Length

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_other_attributes
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import Guild, GUILD_OTIT, GUILD_BLANKO, GUILD_SIK, GUILD_OLTO
from app.form_lib.lib import BaseParticipant, EnumAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices, get_guild_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info


# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Fragment LAN 2024"
_is_enabled = True
_start_date = datetime(2024, 11, 2, 13, 37, 00)
_end_date = datetime(2024, 11, 10, 23, 59, 59)


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()

        result = ""
        if reserve:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut Fragment LAN -tapahtumaan. Olet varasijalla. ",
                "Jos KMP:lle jää peruutuksien myötä vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nTähän sähköpostiin ei voi vastata."
            ])
        else:
            result = ' '.join([
                make_greet_line(recipient),
                "\nOlet varannut konepaikan Fragment LAN -tapahtumaan. Tässä vielä syöttämäsi tiedot: ",
                "\n\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email,
                "\n\nJos tulee kysyttävää, voit olla yhteydessä sähköpostitse taru@otit.fi, tai Telegramissa @AKoponen."
                "\n\nTähän sähköpostiin ei voi vastata."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota('Konepaikka', 60, 100),
    ]


def hide_title():
    return True

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

_GuildEnum = choices_to_enum(_form_name,
                             'guild',
                             get_guild_choices([
                                 Guild(GUILD_OTIT),
                                 Guild(GUILD_BLANKO),
                                 Guild(GUILD_SIK),
                                 Guild(GUILD_OLTO)
                             ]))

_GuildEnumAttribute = EnumAttribute('guild', 'Kilta', 'Kilta', _GuildEnum, validators=[InputRequired()])

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    _GuildEnumAttribute
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
