from datetime import datetime
from typing import Any

from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.forms import basic_form, PhoneNumberField, guild_field, show_name_consent_field, \
    binding_registration_consent_field
from .forms_util.guilds import *
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.models import BasicModel, GuildColumn, BindingRegistrationConsentColumn, PhoneNumberColumn

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


class _Form(basic_form(), PhoneNumberField, guild_field(get_guild_choices(get_all_guilds())),
            show_name_consent_field(), binding_registration_consent_field()):
    pass


class _Model(BasicModel, PhoneNumberColumn, GuildColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name


class _Controller(FormController):

    def __init__(self):
        event = Event('Slumberparty ilmoittautuminen', datetime(2020, 10, 21, 12, 00, 00), datetime(2020, 10, 27, 23, 59, 59), 50, 0)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def post_request_handler(self, request) -> Any:
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.firstname == firstname and entry.lastname == lastname:
                return True
        return False

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: _Form, reserve: bool) -> str:
        firstname = str(form.etunimi.data)
        lastname = str(form.sukunimi.data)
        return ' '.join(["\"Hei", firstname, " ", lastname,
                         "\n\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", firstname, " ", lastname,
                         "\nSähköposti: ", str(form.email.data),
                         "\nPuhelinnumero: ", str(form.phone.data),
                         "\nKilta: ", str(form.kilta.data),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('etunimi', 'etunimi'),
        ('sukunimi', 'sukunimi'),
        ('phone_number', 'phone'),
        ('email', 'email'),
        ('guild_name', 'kilta'),
        ('show_name_consent', 'hyväksyn nimen julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova'),
        ('datetime', 'datetime'),
    ]
    return DataTableInfo(table_structure)
