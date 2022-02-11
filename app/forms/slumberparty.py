from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from typing import Any
from .forms_util.forms import get_guild_choices
from .forms_util.guilds import *
from .forms_util.event import Event
from .forms_util.form_controller import FormController


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
    __tablename__ = 'slumberparty'
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


class SlumberPartyController(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()

        return self._render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        return self._post_routine(_Form(), _Model)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'slumberparty/data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Slumberparty', datetime(2020, 10, 21, 12, 00, 00), datetime(2020, 10, 27, 23, 59, 59), 50, 0)

    def _render_form(self, entries, count: int, event: Event, nowtime, form: FlaskForm) -> Any:
        return render_template('slumberparty/index.html',
                               title='slumberparty ilmoittautuminen',
                               entrys=entries,
                               count=count,
                               starttime=event.get_start_time(),
                               endtime=event.get_end_time(),
                               nowtime=nowtime,
                               limit=event.get_participant_limit(),
                               form=form,
                               page="slumberparty")

    def _find_from_entries(self, entries, form: FlaskForm) -> bool:
        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                return True
        return False

    def _get_email_subject(self) -> str:
        return "slumberparty ilmoittautuminen"

    def _get_email_recipient(self, form: FlaskForm) -> str:
        return str(form.email.data)

    def _get_email_msg(self, form: FlaskForm, reserve: bool) -> str:
        return ' '.join(["\"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                        "\n\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
                        "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                        "\nSähköposti: ", str(form.email.data),
                        "\nPuhelinnumero: ", str(form.phone.data),
                        "\nKilta: ", str(form.kilta.data),
                        "\n\nÄlä vastaa tähän sähköpostiin",
                        "\n\nTerveisin: ropottilari\""])

    def _form_to_model(self, form: FlaskForm, nowtime) -> db.Model:
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
