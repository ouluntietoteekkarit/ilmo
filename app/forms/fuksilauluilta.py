from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any

from app import db
from .forms_util.event import Event
from .forms_util.form_controller import FormController
from .forms_util.form_module_info import ModuleInfo, file_path_to_form_name
from .forms_util.forms import DataTableInfo


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

"""Singleton instance containing this form module's information."""
_form_module = None


def get_module_info() -> ModuleInfo:
    """
    Returns this form's module information.
    """
    global _form_module
    if _form_module is None:
        _form_module = ModuleInfo(_Controller, True, file_path_to_form_name(__file__))
    return _form_module

# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent1 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class _Model(db.Model):
    __tablename__ = 'fuksilauluilta'
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent1 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


class _Controller(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()

        return self._render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        return self._post_routine(_Form(), _Model)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(get_module_info(), _Model)

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Fuksilauluilta', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 13, 23, 59, 59), 70, 0)

    def _render_form(self, entries, participant_count: int, event, nowtime, form):
        return render_template('fuksilauluilta/index.html',
                               title='fuksilauluilta ilmoittautuminen',
                               entrys=entries,
                               participant_count=participant_count,
                               starttime=event.get_start_time(),
                               endtime=event.get_end_time(),
                               nowtime=nowtime,
                               limit=event.get_participant_limit(),
                               form=form,
                               page="fuksilauluilta",
                               form_info=get_module_info())

    def _find_from_entries(self, entries, form: _Form) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                return True
        return False

    def _get_email_subject(self) -> str:
        return 'fuksilauluilta ilmoittautuminen'

    def _get_email_recipient(self, form: _Form) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: FlaskForm, reserve: bool) -> str:
        firstname = str(form.etunimi.data)
        lastname = str(form.sukunimi.data)
        return ' '.join(["\"Hei", firstname, " ", lastname,
                         "\n\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
                         "\n'Nimi: ", firstname, " ", lastname,
                         "\nSähköposti: ", str(form.email.data),
                         "\n\nÄlä vastaa tähän sähköpostiin",
                         "\n\nTerveisin: ropottilari\""])

    def _form_to_model(self, form: FlaskForm, nowtime) -> db.Model:
        return _Model(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            consent1=form.consent1.data,
            datetime=nowtime,
        )

    def _get_data_table_info(self) -> DataTableInfo:
        # MEMO: Order of these two arrays must sync. Order of _Model attributes matters.
        table_headers = ['etunimi', 'sukunimi', 'email', 'hyväksyn tietosuojaselosteen', 'datetime']
        model_attributes = _Model.__table__.columns.keys()[1:]
        return DataTableInfo(table_headers, model_attributes)