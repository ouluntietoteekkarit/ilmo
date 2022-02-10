from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv
from .forms_util.event import Event


class FuksilauluiltaForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent1 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class FuksilauluiltaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent1 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


def fuksilauluilta_handler(request):
    form = FuksilauluiltaForm()
    event = Event('Fuksilauluilta', datetime(2020, 10, 7, 12, 00, 00), datetime(2024, 10, 13, 23, 59, 59), 70)

    nowtime = datetime.now()
    entrys = FuksilauluiltaModel.query.all()
    count = FuksilauluiltaModel.query.count()

    for entry in entrys:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data):
            flash('Olet jo ilmoittautunut')
            return render_form(entrys, count, event, nowtime, form)

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and count <= event.get_participant_limit():
        flash('Ilmoittautuminen onnistui')
        sub = FuksilauluiltaModel(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            consent1=form.consent1.data,
            datetime=nowtime,
        )
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for('route_fuksilauluilta'))

    elif submitted and count > event.get_participant_limit():
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_form(entrys, count, event, nowtime, form)


def render_form(entrys, count, event, nowtime, form):
    return render_template('fuksilauluilta/fuksilauluilta.html',
                           title='fuksilauluilta ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="fuksilauluilta")

def fuksilauluilta_data():
    limit = 70
    entries = FuksilauluiltaModel.query.all()
    count = FuksilauluiltaModel.query.count()
    return render_template('fuksilauluilta/fuksilauluilta_data.html',
                           title='fuksilauluilta data',
                           entries=entries,
                           count=count,
                           limit=limit)


def fuksilauluilta_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('fuksilauluilta_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='fuksilauluilta_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
