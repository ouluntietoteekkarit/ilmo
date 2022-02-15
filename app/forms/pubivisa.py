from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import List

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line, make_fullname_line
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import ShowNameConsentField, BindingRegistrationConsentField, BasicForm, PhoneNumberField, \
    GuildField, get_guild_choices
from .forms_util.guilds import *
from .forms_util.form_controller import FormController, DataTableInfo, Event
from .forms_util.models import BasicModel, BindingRegistrationConsentColumn, basic_model_csv_map, \
    binding_registration_csv_map, PhoneNumberColumn, GuildColumn, phone_number_csv_map, guild_name_csv_map

_form_name = file_path_to_form_name(__file__)


@BindingRegistrationConsentField()
@ShowNameConsentField('Sallin joukkueen nimen julkaisemisen osallistujalistassa')
@GuildField(get_guild_choices(get_all_guilds()))
@PhoneNumberField()
class _Form(BasicForm):
    teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone1 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email1 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta1 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone2 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email2 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta2 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

    etunimi3 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi3 = StringField('Sukunimi', validators=[length(max=50)])
    phone3 = StringField('Puhelinnumero', validators=[length(max=20)])
    email3 = StringField('Sähköposti', validators=[length(max=100)])
    kilta3 = SelectField('Kilta', choices=get_guild_choices(get_all_guilds()))

    def get_participant_count(self) -> int:
        return int(self.firstname.data and self.lastname.data) \
               + int(self.etunimi1.data and self.sukunimi1.data) \
               + int(self.etunimi2.data and self.sukunimi2.data) \
               + int(self.etunimi3.data and self.sukunimi3.data)


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


class _Controller(FormController):

    def _count_participants(self, entries) -> int:
        total_count = 0
        for entry in entries:
            total_count += entry.personcount
        return total_count

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
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
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
               datetime(2020, 10, 10, 23, 59, 59), 50, 0, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, False, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
