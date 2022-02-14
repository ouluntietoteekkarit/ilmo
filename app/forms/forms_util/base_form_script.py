from datetime import datetime
from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations
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
        return ""


_data_table_info = DataTableInfo(basic_model_csv_map())
_event = Event(, _Form.asks_name_consent)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    if not hasattr(get_module_info, 'result'):
        get_module_info.result = ModuleInfo(_Controller, True, _form_name, FormContext(_event, _Form, _Model, _data_table_info))
    return get_module_info.result

# P U B L I C   M O D U L E   I N T E R F A C E   E N D
