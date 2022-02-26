from datetime import datetime

from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.forms import ShowNameConsentField, BindingRegistrationConsentField, BasicForm, get_guild_choices
from .forms_util.forms import GuildField, PhoneNumberField
from .forms_util.guilds import *
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.form_controller import FormController, DataTableInfo, Event, Quota
from .forms_util.models import BasicModel, PhoneNumberColumn, GuildColumn, basic_model_csv_map, \
    binding_registration_csv_map, guild_name_csv_map, phone_number_csv_map
from .forms_util.models import BindingRegistrationConsentColumn

_form_name = file_path_to_form_name(__file__)


@BindingRegistrationConsentField()
@ShowNameConsentField()
@GuildField(get_guild_choices(get_all_guilds()))
@PhoneNumberField()
class _Form(BasicForm):
    pass


class _Model(BasicModel, PhoneNumberColumn, GuildColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
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
_event = Event('Kortti- ja lautapeli-ilta', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 13, 23, 59, 59), [Quota.default_quota(50, 0)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D