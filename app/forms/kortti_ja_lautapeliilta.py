from datetime import datetime
from typing import Any

from .forms_util.forms import basic_form, show_name_consent_field, binding_registration_consent_field
from .forms_util.forms import guild_field, PhoneNumberField
from .forms_util.guilds import *
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.guilds import get_guild_choices
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.models import BasicModel, PhoneNumberColumn, GuildColumn
from .forms_util.models import BindingRegistrationConsentColumn

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

"""Singleton instance containing this form module's information."""
_form_module = None
_form_name = file_path_to_form_name(__file__)


def get_module_info() -> ModuleInfo:
    """
    Returns this form's module information.
    """
    global _form_module
    if _form_module is None:
        _form_module = ModuleInfo(_Controller, True, _form_name)
    return _form_module

# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Form(basic_form(), show_name_consent_field(), binding_registration_consent_field(),
            guild_field(get_guild_choices(get_all_guilds())), PhoneNumberField):
    pass


class _Model(BasicModel, PhoneNumberColumn, GuildColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


class _Controller(FormController):

    def __init__(self):
        event = Event('Kortti- ja lautapeli-ilta ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 13, 23, 59, 59), 50, 0)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def _get_email_recipient(self, model: _Model) -> str:
        return model.get_email()

    def _get_email_msg(self, model: _Model, reserve: bool) -> str:
        firstname = model.get_firstname()
        lastname = model.get_lastname()
        return ' '.join(["\"Hei", firstname, " ", lastname,
                         "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", firstname, " ", lastname,
                         "\nSähköposti: ", model.get_email(),
                         "\nPuhelinnumero: ", model.get_phone_number(),
                         "\nKilta: ", model.get_guild_name(),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('phone_number', 'phone'),
        ('email', 'email'),
        ('guild_name', 'kilta'),
        ('show_name_consent', 'hyväksyn nimen julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
