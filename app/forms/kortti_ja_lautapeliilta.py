from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any

from app import db
from .forms_util.guilds import *
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.guilds import get_guild_choices
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

"""Singleton instance containing this form module's information."""
_form_module = None
_form_name = file_path_to_form_name(__file__)


def get_module_info() -> ModuleInfo:
    """
    Returns this form's module information.
    """
    global _form_module
    if _form_module is None:
        _form_module = ModuleInfo(_Controller, True, _form_name)
    return _form_module

# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta = SelectField('Kilta *', choices=get_guild_choices(get_all_guilds()))
    consent0 = BooleanField('Sallin nimeni julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = _form_name
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    email = db.Column(db.String(128))
    kilta = db.Column(db.String(16))
    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    consent2 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())

    def get_firstname(self) -> str:
        return self.etunimi

    def get_lastname(self) -> str:
        return self.sukunimi

    def get_email(self) -> str:
        return self.email

    def get_show_name_consent(self) -> bool:
        return self.consent0


class _Controller(FormController):

    def __init__(self):
        event = Event('Kortti- ja lautapeli-ilta ilmoittautuminen', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 13, 23, 59, 59), 50, 0)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def post_request_handler(self, request) -> Any:
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                return True
        return False

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: _Form, reserve: bool) -> str:
        firstname = str(form.etunimi.data)
        lastname = str(form.sukunimi.data)
        return ' '.join(["\"Hei", firstname, " ", lastname,
                         "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", firstname, " ", lastname,
                         "\nSähköposti: ", str(form.email.data),
                         "\nPuhelinnumero: ", str(form.phone.data),
                         "\nKilta: ", str(form.kilta.data),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])

    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        return _Model(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            phone=form.phone.data,
            email=form.email.data,
            kilta=form.kilta.data,
            consent0=form.consent0.data,
            consent1=form.consent1.data,
            consent2=form.consent2.data,
            datetime=nowtime
        )


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('etunimi', 'etunimi'),
        ('sukunimi', 'sukunimi'),
        ('phone', 'phone'),
        ('email', 'email'),
        ('kilta', 'kilta'),
        ('consent0', 'hyväksyn nimen julkaisemisen'),
        ('consent1', 'hyväksyn tietosuojaselosteen'),
        ('consent2', 'ymmärrän että ilmoittautuminen on sitova'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
