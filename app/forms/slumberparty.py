from datetime import datetime

from wtforms import Form
from wtforms.validators import InputRequired

from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.common_attributes import make_attribute_quota, make_attribute_phone_number, make_attribute_email, \
    make_attribute_lastname, make_attribute_firstname, make_attribute_name_consent, \
    make_attribute_binding_registration_consent, make_attribute_privacy_consent
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.guilds import *
from app.form_lib.form_controller import FormController, DataTableInfo, Event
from app.form_lib.lib import Quota
from app.form_lib.models import RegistrationModel, basic_model_csv_map, phone_number_csv_map, guild_name_csv_map, \
    binding_registration_csv_map
from app.form_lib.util import make_types, choices_to_enum, get_guild_choices

_form_name = file_path_to_form_name(__file__)

_GuildEnum = choices_to_enum(_form_name, 'guild', get_guild_choices(get_all_guilds()))

participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
    make_attribute_phone_number(),
    make_attribute_quota(_GuildEnum, 'Kilta *', 'Kilta')
]
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_binding_registration_consent(),
    make_attribute_privacy_consent()
]
types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)
_Form = types.get_form_type()
_Model = types.get_model_type()


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
            "\nNimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email_address(),
            "\nPuhelinnumero: ", model.get_phone_number(),
            "\nKilta: ", model.get_guild_name(),
            "\n\n", make_signature_line()
        ])


# MEMO: (attribute, header_text)
_data_table_info = DataTableInfo(basic_model_csv_map() +
                                 phone_number_csv_map() +
                                 guild_name_csv_map() +
                                 binding_registration_csv_map())
_event = Event('Slumberparty', datetime(2020, 10, 21, 12, 00, 00),
               datetime(2020, 10, 27, 23, 59, 59), [Quota.default_quota(50, 0)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
