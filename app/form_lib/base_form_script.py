from datetime import datetime
from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations
from app.form_lib.lib import Quota
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.forms import RegistrationForm
from app.form_lib.models import RegistrationModel, basic_model_csv_map

_form_name = make_form_name(__file__)


class _Form(RegistrationForm):
    pass


class _Model(RegistrationModel):
    __tablename__ = _form_name


class _Controller(FormController):
    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        return ""


_data_table_info = DataTableInfo(basic_model_csv_map())
_event = Event('---', datetime(----),
               datetime(----), -, types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _Form, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
