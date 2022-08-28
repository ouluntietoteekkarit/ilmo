from datetime import datetime
from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.form_controller import FormController, FormContext, DataTableInfo, EventRegistrations
from app.form_lib.event import Event
from app.form_lib.lib import BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.forms import RegistrationForm
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.util import make_types
from app.form_lib.models import RegistrationModel


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        return ""


_form_name = make_form_name(__file__)

participant_attributes = []
optional_participant_attributes = []
other_attributes = []

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('---', datetime(----),
               datetime(----), -, _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)



