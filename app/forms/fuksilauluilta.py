from datetime import datetime

from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import BasicForm
from .forms_util.models import BasicModel, basic_model_csv_map

_form_name = file_path_to_form_name(__file__)


class _Form(BasicForm):
    pass


class _Model(BasicModel):
    __tablename__ = _form_name


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
            "\n'Nimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email_address(),
            "\n\n", make_signature_line()
        ])


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    return DataTableInfo(basic_model_csv_map())


_event = Event('Fuksilauluilta ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00), datetime(2026, 10, 13, 23, 59, 59), 70, 0, _Form.asks_name_consent)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    if not hasattr(get_module_info, 'result'):
        get_module_info.result = ModuleInfo(_Controller, True, _form_name, FormContext(_event, _Form, _Model, _get_data_table_info()))
    return get_module_info.result

# P U B L I C   M O D U L E   I N T E R F A C E   E N D
