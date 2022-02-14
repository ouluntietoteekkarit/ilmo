from datetime import datetime

from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.forms import basic_form, show_name_consent_field, binding_registration_consent_field
from .forms_util.forms import guild_field, PhoneNumberField
from .forms_util.guilds import *
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.guilds import get_guild_choices
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.models import BasicModel, PhoneNumberColumn, GuildColumn
from .forms_util.models import BindingRegistrationConsentColumn

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
    return _form_module
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


_name_consent_type = show_name_consent_field()
class _Form(basic_form(),
            PhoneNumberField,
            guild_field(get_guild_choices(get_all_guilds())),
            _name_consent_type,
            binding_registration_consent_field()):
    pass


class _Model(BasicModel, PhoneNumberColumn, GuildColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


_event = Event('Kortti- ja lautapeli-ilta ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 13, 23, 59, 59), 50, 0, issubclass(_Form, _name_consent_type))


class _Controller(FormController):

    def __init__(self):
        super().__init__(_event, _Form, _Model, get_module_info(), _get_data_table_info())

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
            "\n'Nimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email(),
            "\nPuhelinnumero: ", model.get_phone_number(),
            "\nKilta: ", model.get_guild_name(),
            "\n\n", make_signature_line()
        ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo([
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('phone_number', 'phone'),
        ('email', 'email'),
        ('guild_name', 'kilta'),
        ('show_name_consent', 'hyväksyn nimen julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova'),
        ('datetime', 'datetime')
    ])
