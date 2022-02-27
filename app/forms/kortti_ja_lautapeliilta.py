from __future__ import annotations
from datetime import datetime

from app.email import make_greet_line, make_signature_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_phone_number, make_attribute_name_consent, make_attribute_privacy_consent, \
    make_attribute_binding_registration_consent
from app.form_lib.guilds import *
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.form_controller import FormController, Event
from app.form_lib.lib import Quota, BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_guild_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
            "\nNimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email(),
            "\nPuhelinnumero: ", recipient.get_phone_number(),
            "\nKilta: ", recipient.get_quota(),
            "\n\n", make_signature_line()
        ])


_form_name = make_form_name(__file__)
_GuildEnum = choices_to_enum(_form_name, 'guild', get_guild_choices(get_all_guilds()))
participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
] + [
    make_attribute_phone_number(),
    make_attribute_quota(_GuildEnum, 'Kilta *', 'Kilta')
]
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(),
    make_attribute_binding_registration_consent()
]
_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)
_Form = _types.get_form_type()
_Model = _types.get_model_type()

_event = Event('Kortti- ja lautapeli-ilta', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 13, 23, 59, 59), [Quota.default_quota(50, 0)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)
