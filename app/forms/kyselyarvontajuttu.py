from flask_wtf import FlaskForm
from flask import render_template, flash
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from typing import Any

from app import db
from .forms_util.event import Event
from .forms_util.form_controller import FormController
from .forms_util.form_module import FormModule, file_path_to_form_name


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T

def get_form_info() -> FormModule:
    """
    Returns this form's module information.
    """
    return FormModule(_Controller, True, file_path_to_form_name(__file__))

# P U B L I C   M O D U L E   I N T E R F A C E   E N D


class _Form(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent0 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön *',
                            validators=[DataRequired()])
    submit = SubmitField('Submit')


class _Model(db.Model):
    __tablename__ = 'kysely_arvonta_juttu'
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent0 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


class _Controller(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()

        return self._render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        count = len(entries)

        if count >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            return self._render_form(entries, count, event, nowtime, form)

        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        email = form.email.data
        for entry in entries:
            if (entry.etunimi == firstname and entry.sukunimi == lastname) or entry.email == email:
                flash('Olet jo ilmoittautunut')
                return self._render_form(entries, count, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(self._form_to_model(form, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            # return redirect(url_for('route_get_kysely_arvonta_juttu'))
            return render_template('kysely_arvonta_juttu/redirect.html')

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return self._render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'kysely_arvonta_juttu/data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Hyvinvointi- ja etäopiskelukysely arvonta', datetime(2020, 11, 2, 12, 00, 00),
                     datetime(2020, 11, 23, 23, 59, 59), 4000, 0)

    def _render_form(self, entries, count: int, event: Event, nowtime, form: _Form) -> Any:
        return render_template('kysely_arvonta_juttu/index.html',
                               title='kysely_arvonta_juttu ilmoittautuminen',
                               entrys=entries,
                               count=count,
                               starttime=event.get_start_time(),
                               endtime=event.get_end_time(),
                               nowtime=nowtime,
                               limit=event.get_participant_limit(),
                               form=form,
                               page="kysely_arvonta_juttu")

    def _find_from_entries(self, entries, form: FlaskForm) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        email = form.email.data
        for entry in entries:
            if (entry.etunimi == firstname and entry.sukunimi == lastname) or entry.email == email:
                return True
        return False

    def _get_email_subject(self) -> str:
        return "hyvinvointi- ja etäopiskelukysely"

    def _get_email_recipient(self, form: FlaskForm) -> str:
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
