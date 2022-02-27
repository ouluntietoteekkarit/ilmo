from __future__ import annotations
from datetime import datetime
from typing import List, Iterable

from app.email import make_greet_line, make_signature_line, make_fullname_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_phone_number, make_attribute_quota, make_attribute_name_consent, \
    make_attribute_binding_registration_consent, make_attribute_privacy_consent
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import *
from app.form_lib.form_controller import FormController, Event
from app.form_lib.lib import Quota, StringAttribute, BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.util import make_types, choices_to_enum, get_guild_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        participants = list(model.get_required_participants()) + list(model.get_optional_participants())
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
            "\nJoukkueen nimi: ", model.get_other_attributes().teamname,
            "\nOsallistujien nimet:\n"] +
            [make_fullname_line(participant.get_firstname(), participant.get_lastname()) for participant in participants] +
            ["\n\n", make_signature_line()])


def _make_attribute_teamname(validators: Iterable = None):
    return StringAttribute('teamname', 'Joukkueen nimi *', 'Joukkueen nimi', 100, validators=validators)


_form_name = make_form_name(__file__)
_GuildEnum = choices_to_enum(_form_name, 'guild', get_guild_choices(get_all_guilds()))

required_participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
    make_attribute_phone_number(),
    make_attribute_quota(_GuildEnum, 'Kilta *', 'Kilta'),
]
optional_participant_attributes = required_participant_attributes
other_attributes = [
    _make_attribute_teamname(),
    make_attribute_name_consent('Sallin joukkueen nimen julkaisemisen osallistujalistassa'),
    make_attribute_binding_registration_consent(),
    make_attribute_privacy_consent()
]

_types = make_types(required_participant_attributes, optional_participant_attributes, other_attributes, 3, 1, _form_name)
_Form = _types.get_form_type()
_Model = _types.get_model_type()


_event = Event('Pubivisa ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 10, 23, 59, 59), [Quota.default_quota(50, 0)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)


