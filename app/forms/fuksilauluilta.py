from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from typing import Any
from .forms_util.event import Event
from .forms_util.form_controller import FormController


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


class FuksiLauluIltaController(FormController):

    def get_request_handler(self, request) -> Any:
        form = _Form()
        event = self._get_event()
        entries = _Model.query.all()

        return _render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        form = _Form()
        event = self._get_event()
        nowtime = datetime.now()
        entries = _Model.query.all()
        count = len(entries)

        if count >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            return _render_form(entries, count, event, nowtime, form)

        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        for entry in entries:
            if entry.etunimi == firstname and entry.sukunimi == lastname:
                flash('Olet jo ilmoittautunut')
                return _render_form(entries, count, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(_form_to_model(form, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            return redirect(url_for('route_get_fuksilauluilta'))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(_Model, 'fuksilauluilta/fuksilauluilta_data.html', )

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(_Model.__tablename__)

    def _get_event(self) -> Event:
        return Event('Fuksilauluilta', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 13, 23, 59, 59), 70)


def _form_to_model (form, nowtime):
    return _Model(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        email=form.email.data,
        consent1=form.consent1.data,
        datetime=nowtime,
    )


def _render_form(entries, count, event, nowtime, form):
    return render_template('fuksilauluilta/fuksilauluilta.html',
                           title='fuksilauluilta ilmoittautuminen',
                           entrys=entries,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="fuksilauluilta")
