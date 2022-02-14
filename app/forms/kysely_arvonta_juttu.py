from flask import render_template
from datetime import datetime
from typing import Any

from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.forms import BasicForm
from .forms_util.models import BasicModel


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
    return _form_module
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Form(BasicForm):
    pass


class _Model(BasicModel):
    __tablename__ = _form_name


_event = Event('Hyvinvointi- ja etäopiskelukysely arvonta ilmoittautuminen', datetime(2020, 11, 2, 12, 00, 00), datetime(2020, 11, 23, 23, 59, 59), 4000, 0, _Form.asks_name_consent)


class _Controller(FormController):

    def __init__(self):
        super().__init__(_event, _Form, _Model, get_module_info(), _get_data_table_info())

    def _post_routine_output(self, registrations: EventRegistrations, form: _Form, nowtime) -> Any:
        return render_template('kysely_arvonta_juttu/redirect.html')

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet jättänyt yhteystietosi hyvinvointi- ja etäopiskelukyselyn arvontaan. Syötit seuraavia tietoja: ",
            "\n'Nimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email_address(),
            "\n\n", make_signature_line()
        ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo([
        ('firstname', 'etunimi'),
        ('lastname', 'sukunimi'),
        ('email', 'email'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ])
