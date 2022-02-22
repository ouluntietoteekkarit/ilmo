from wtforms import StringField
from wtforms.validators import DataRequired, length, InputRequired
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line, make_fullname_line
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import get_guild_choices, FormBuilder, ParticipantFormBuilder, \
    make_field_binding_registration_consent, make_field_name_consent, make_field_quota, make_field_phone_number, \
    make_field_email, make_field_lastname, make_field_firstname, make_field_required_participants, \
    make_field_optional_participants, make_field_privacy_consent
from .forms_util.guilds import *
from .forms_util.form_controller import FormController, DataTableInfo, Event, Quota
from .forms_util.models import BasicModel, BindingRegistrationConsentColumn, basic_model_csv_map, \
    binding_registration_csv_map, PhoneNumberColumn, GuildColumn, phone_number_csv_map, guild_name_csv_map

_form_name = file_path_to_form_name(__file__)


_Participant = ParticipantFormBuilder().add_fields([
    make_field_firstname([InputRequired()]),
    make_field_lastname([InputRequired()]),
    make_field_email([InputRequired()]),
    make_field_phone_number([InputRequired()]),
    make_field_quota('Kilta *', get_guild_choices(get_all_guilds()), [InputRequired()]),
]).build()

_Form = FormBuilder().add_fields([
    make_field_required_participants(_Participant, 3),
    make_field_optional_participants(_Participant, 1),
    make_field_name_consent('Sallin joukkueen nimen julkaisemisen osallistujalistassa'),
    make_field_binding_registration_consent(),
    make_field_privacy_consent()
]).build()

_Form.teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])


class _Model(BasicModel, PhoneNumberColumn, GuildColumn, BindingRegistrationConsentColumn):
    __tablename__ = _form_name
    teamname = db.Column(db.String(128))

    kilta0 = db.Column(db.String(16))

    etunimi1 = db.Column(db.String(64))
    sukunimi1 = db.Column(db.String(64))
    phone1 = db.Column(db.String(32))
    email1 = db.Column(db.String(128))
    kilta1 = db.Column(db.String(16))

    etunimi2 = db.Column(db.String(64))
    sukunimi2 = db.Column(db.String(64))
    phone2 = db.Column(db.String(32))
    email2 = db.Column(db.String(128))
    kilta2 = db.Column(db.String(16))

    etunimi3 = db.Column(db.String(64))
    sukunimi3 = db.Column(db.String(64))
    phone3 = db.Column(db.String(32))
    email3 = db.Column(db.String(128))
    kilta3 = db.Column(db.String(16))

    personcount = db.Column(db.Integer())

    def get_participant_count(self) -> int:
        return int(bool(self.firstname and self.lastname)) \
             + int(bool(self.etunimi1 and self.sukunimi1)) \
             + int(bool(self.etunimi2 and self.sukunimi2)) \
             + int(bool(self.etunimi3 and self.sukunimi3))

    def get_quota_counts(self) -> List[Quota]:
        return [
            Quota(self.kilta0, int(bool(self.firstname and self.lastname))),
            Quota(self.kilta1, int(bool(self.etunimi1 and self.sukunimi1))),
            Quota(self.kilta2, int(bool(self.etunimi2 and self.sukunimi2))),
            Quota(self.kilta3, int(bool(self.etunimi3 and self.sukunimi3))),
        ]


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_recipient(self, model: _Model) -> List[EmailRecipient]:
        return [
            EmailRecipient(model.get_firstname(), model.get_lastname(), model.get_email()),
            EmailRecipient(model.etunimi1, model.sukunimi1, model.email1),
            EmailRecipient(model.etunimi2, model.sukunimi2, model.email2),
            EmailRecipient(model.etunimi3, model.sukunimi3, model.email3)
        ]

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        return ' '.join([
            make_greet_line(recipient),
            "\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
            "\nJoukkueen nimi: ", model.teamname,
            "\nOsallistujien nimet:\n",
            make_fullname_line(model.get_firstname(), model.get_lastname()),
            make_fullname_line(model.etunimi1, model.sukunimi1),
            make_fullname_line(model.etunimi2, model.sukunimi2),
            make_fullname_line(model.etunimi3, model.sukunimi3), "\n",
            "\n\n", make_signature_line()
        ])

    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        model = super()._form_to_model(form, nowtime)
        model.personcount = form.get_participant_count()
        return model


# MEMO: (attribute, header_text)
# MEMO: Exclude id, teamname and person count
_data_table_info = DataTableInfo(
    basic_model_csv_map() +
    binding_registration_csv_map() +
    phone_number_csv_map() +
    guild_name_csv_map() +
    [('etunimi1', 'etunimi1'),
     ('sukunimi1', 'sukunimi1'),
     ('email1', 'email1'),
     ('phone1', 'phone1'),
     ('kilta1', 'kilta1'),
     ('etunimi2', 'etunimi2'),
     ('sukunimi2', 'sukunimi2'),
     ('email2', 'email2'),
     ('phone2', 'phone2'),
     ('kilta2', 'kilta2'),
     ('etunimi3', 'etunimi3'),
     ('sukunimi3', 'sukunimi3'),
     ('email3', 'email3'),
     ('phone3', 'phone3'),
     ('kilta3', 'kilta3')])
_event = Event('Pubivisa ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 10, 23, 59, 59), [Quota.default_quota(50, 0)], _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
