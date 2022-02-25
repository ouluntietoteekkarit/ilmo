from datetime import datetime
from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations, Quota
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.forms import BasicForm
from app.form_lib.models import BasicModel, basic_model_csv_map

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
_event = Event('---', datetime(----),
               datetime(----), -, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
