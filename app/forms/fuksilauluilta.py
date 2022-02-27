from datetime import datetime

from app.email import EmailRecipient, make_greet_line, make_signature_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, \
    make_attribute_email, make_attribute_privacy_consent
from app.form_lib.form_controller import FormController, Event
from app.form_lib.lib import Quota
from app.form_lib.form_module import ModuleInfo, file_path_to_form_name
from app.form_lib.util import make_types, make_data_table_info_from_attributes

_form_name = file_path_to_form_name(__file__)


participant_attributes = [
    make_attribute_firstname(),
    make_attribute_lastname(),
    make_attribute_email(),
]

other_attributes = [
    make_attribute_privacy_consent()
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)
_Form = _types.get_form_type()
_Model = _types.get_model_type()


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
            "\nNimi: ", firstname, " ", lastname,
            "\nSähköposti: ", recipient.get_email_address(),
            "\n\n", make_signature_line()
        ])


_event = Event('Fuksilauluilta', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 13, 23, 59, 59), [Quota.default_quota(70, 0)], _types.asks_name_consent())
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
