from flask import flash
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any, List

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line, make_fullname_line
from .forms_util.form_module import ModuleInfo, init_module
from .forms_util.forms import basic_form, show_name_consent_field, binding_registration_consent_field
from .forms_util.guilds import *
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.models import BasicModel, BindingRegistrationConsentColumn

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
(_form_module, _form_name) = init_module(__file__)


def get_module_info() -> ModuleInfo:
    """Returns a singleton object containing this form's module information."""
    global _form_module
    _form_module = _form_module or ModuleInfo(_Controller, True, _form_name)
    return _form_module
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_name_consent_txt = 'Sallin joukkueen nimen julkaisemisen osallistujalistassa'
_name_consent_type = show_name_consent_field(_name_consent_txt)
class _Form(basic_form(),
            _name_consent_type,
            binding_registration_consent_field()):
    teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])

    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    kilta0 = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()), validators=[DataRequired()])

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


class _Model(BasicModel, BindingRegistrationConsentColumn):
    __tablename__ = _form_name
    teamname = db.Column(db.String(128))

    phone0 = db.Column(db.String(32))
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


_event = Event('Pubivisa ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00),
               datetime(2020, 10, 10, 23, 59, 59), 50, 0, issubclass(_Form, _name_consent_type))


class _Controller(FormController):

    def __init__(self):
        super().__init__(_event, _Form, _Model, get_module_info(), _get_data_table_info())

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        totalcount = self._count_participants(entries)
        group_size = self._count_members(form)
        totalcount += group_size

        error_msg = self._check_form_submit(event, form, entries, nowtime, totalcount)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(entries, event, nowtime, form,
                                           participant_count=totalcount)

        model = self._form_to_model(form, nowtime)
        if self._insert_model(model):
            flash('Ilmoittautuminen onnistui')

        return self._render_index_view(entries, event, nowtime, form, participant_count=totalcount)

    def _render_index_view(self, entries, event: Event, nowtime, form: _Form, **extra_template_args) -> Any:
        participant_count = self._count_participants(entries)
        return super()._render_index_view(entries, event, nowtime, form, **{
            'participant_count': participant_count,
            **extra_template_args})

    def _count_participants(self, entries) -> int:
        total_count = 0
        for entry in entries:
            total_count += entry.personcount
        return total_count

    # MEMO: "Evil" Covariant parameter
    def _get_email_recipient(self, recipient, model: _Model) -> List[EmailRecipient]:
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
            "\n'Joukkueen nimi: ", model.teamname,
            "\n'Osallistujien nimet:\n",
            make_fullname_line(model.get_firstname(), model.get_lastname()),
            make_fullname_line(model.etunimi1, model.sukunimi1),
            make_fullname_line(model.etunimi2, model.sukunimi2),
            make_fullname_line(model.etunimi3, model.sukunimi3), "\n",
            "\n\n", make_signature_line()
        ])

    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        model = super()._form_to_model(form, nowtime)
        members = self._count_members(form)
        model.personcount = members
        return model

    def _count_members(self, form: _Form) -> int:
        members = 0
        members += int(form.etunimi0.data and form.sukunimi0.data)
        members += int(form.etunimi1.data and form.sukunimi1.data)
        members += int(form.etunimi2.data and form.sukunimi2.data)
        members += int(form.etunimi3.data and form.sukunimi3.data)
        return members


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    # MEMO: Exclude id, teamname and person count
    return DataTableInfo([
        ('firstname', 'etunimi0'),
        ('lastname', 'sukunimi0'),
        ('email', 'email0'),
        ('phone0', 'phone0'),
        ('kilta0', 'kilta0'),
        ('etunimi1', 'etunimi1'),
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
        ('kilta3', 'kilta3'),
        ('show_name_consent', 'hyväksyn nimen julkaisemisen'),
        ('privacy_consent', 'hyväksyn tietosuojaselosteen'),
        ('binding_registration_consent', 'ymmärrän että ilmoittautuminen on sitova'),
        ('datetime', 'datetime')
    ])
