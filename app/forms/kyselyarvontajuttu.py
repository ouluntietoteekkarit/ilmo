from flask_wtf import FlaskForm
from flask import render_template, flash
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
from app import db
from typing import Any
from .forms_util.guilds import *
from .forms_util.event import Event
from .forms_util.form_controller import FormController


class KyselyArvontaJuttuForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent0 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön *', validators=[DataRequired()])
    submit = SubmitField('Submit')


class KyselyArvontaJuttuModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent0 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


class KyselyArvontaJuttuController(FormController):

    def get_request_handler(self, request) -> Any:
        form = KyselyArvontaJuttuForm()
        event = self._get_event()
        entries = KyselyArvontaJuttuModel.query.all()

        return _render_form(entries, len(entries), event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        form = KyselyArvontaJuttuForm()
        event = self._get_event()
        nowtime = datetime.now()
        entries = KyselyArvontaJuttuModel.query.all()
        count = len(entries)

        if count >= event.get_participant_limit():
            flash('Ilmoittautuminen on jo täynnä')
            return _render_form(entries, count, event, nowtime, form)

        firstname = form.etunimi.data
        lastname = form.sukunimi.data
        email = form.email.data
        for entry in entries:
            if (entry.etunimi == firstname and entry.sukunimi == lastname) or entry.email == email:
                flash('Olet jo ilmoittautunut')
                return _render_form(entries, count, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(_form_to_model(form, nowtime))
            db.session.commit()

            flash('Ilmoittautuminen onnistui')
            # return redirect(url_for('route_get_kysely_arvonta_juttu'))
            return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu_redirect.html')

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return _render_form(entries, count, event, nowtime, form)

    def get_data_request_handler(self, request) -> Any:
        return self._data_view(KyselyArvontaJuttuModel, 'kysely_arvonta_juttu/kysely_arvonta_juttu_data.html')

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(KyselyArvontaJuttuModel.__tablename__)

    def _get_event(self) -> Event:
        return Event('Hyvinvointi- ja etäopiskelukysely arvonta', datetime(2020, 11, 2, 12, 00, 00),
                     datetime(2020, 11, 23, 23, 59, 59), 4000)


def _render_form(entrys, count, event, nowtime, form):
    return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu.html',
                           title='kysely_arvonta_juttu ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="kysely_arvonta_juttu")


def _form_to_model(form, nowtime):
    return KyselyArvontaJuttuModel(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        email=form.email.data,
        consent0=form.consent0.data,
        datetime=nowtime,
    )
