from flask_wtf import FlaskForm
from flask import render_template, flash
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any

from app import db
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name


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
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent0 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön *',
                            validators=[DataRequired()])
    submit = SubmitField('Submit')


class _Model(db.Model):
    __tablename__ = _form_name
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent0 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())

    def get_firstname(self) -> str:
        return self.etunimi

    def get_lastname(self) -> str:
        return self.sukunimi

    def get_email(self) -> str:
        return self.email

    def get_show_name_consent(self) -> bool:
        return False


class _Controller(FormController):

    def __init__(self):
        event = Event('Hyvinvointi- ja etäopiskelukysely arvonta ilmoittautuminen', datetime(2020, 11, 2, 12, 00, 00), datetime(2020, 11, 23, 23, 59, 59), 4000, 0)
        super().__init__(FormContext(event, _Form, _Model, get_module_info(), _get_data_table_info()))

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        count = len(entries)

        error_msg = self._check_form_submit(event, form, entries, nowtime, count)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(entries, event, nowtime, form)

        db.session.add(self._form_to_model(form, nowtime))
        db.session.commit()

        flash('Ilmoittautuminen onnistui')
        return render_template('kysely_arvonta_juttu/redirect.html')
        #return self._render_index_view(entries, event, nowtime, form)

    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        email = form.email.data
        for entry in entries:
            if (entry.etunimi == firstname and entry.sukunimi == lastname) or entry.email == email:
                return True
        return False

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: _Form, reserve: bool) -> str:
        firstname = str(form.etunimi.data)
        lastname = str(form.sukunimi.data)
        return ' '.join(["\"Hei", firstname, " ", lastname,
                         "\n\nOlet jättänyt yhteystietosi hyvinvointi- ja etäopiskelukyselyn arvontaan. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", firstname, " ", lastname,
                         "\nSähköposti: ", str(form.email.data),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])

    def _form_to_model(self, form: _Form, nowtime) -> _Model:
        return _Model(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            consent0=form.consent0.data,
            datetime=nowtime,
        )


def _get_data_table_info() -> DataTableInfo:
    # MEMO: (attribute, header_text)
    table_structure = [
        ('etunimi', 'etunimi'),
        ('sukunimi', 'sukunimi'),
        ('email', 'email'),
        ('consent0', 'hyväksyn tietosuojaselosteen'),
        ('datetime', 'datetime')
    ]
    return DataTableInfo(table_structure)
