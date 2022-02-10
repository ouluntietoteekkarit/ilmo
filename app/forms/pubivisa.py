from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv
from .forms_util.guilds import *
from .forms_util.event import Event


def get_guild_choices():
    choices = []
    for guild in get_all_guilds():
        choices.append((guild.get_name(), guild.get_name()))
    return choices


class PubivisaForm(FlaskForm):
    teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])

    etunimi0 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi0 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email0 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta0 = SelectField('Kilta *', choices=get_guild_choices(), validators=[DataRequired()])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone1 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email1 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta1 = SelectField('Kilta *', choices=get_guild_choices(), validators=[DataRequired()])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone2 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email2 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta2 = SelectField('Kilta *', choices=get_guild_choices(), validators=[DataRequired()])

    etunimi3 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi3 = StringField('Sukunimi', validators=[length(max=50)])
    phone3 = StringField('Puhelinnumero', validators=[length(max=20)])
    email3 = StringField('Sähköposti', validators=[length(max=100)])
    kilta3 = SelectField('Kilta', choices=get_guild_choices())

    consent0 = BooleanField('Sallin joukkueen nimen julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class PubivisaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(128))

    etunimi0 = db.Column(db.String(64))
    sukunimi0 = db.Column(db.String(64))
    phone0 = db.Column(db.String(32))
    email0 = db.Column(db.String(128))
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

    consent0 = db.Column(db.Boolean())
    consent1 = db.Column(db.Boolean())
    consent2 = db.Column(db.Boolean())

    datetime = db.Column(db.DateTime())

    personcount = db.Column(db.Integer())


def get_event():
    return Event('Pubivisa', datetime(2020, 10, 7, 12, 00, 00), datetime(2020, 10, 10, 23, 59, 59), 50)


def pubivisa_handler(request):
    form = PubivisaForm()
    event = get_event()
    nowtime = datetime.now()
    entries = PubivisaModel.query.all()
    group_size = 0
    totalcount = 0
    for entry in entries:
        totalcount += entry.personcount

    for entry in entries:
        if entry.teamname == form.teamname.data:
            flash('Olet jo ilmoittautunut')

            return _render_form(entries, totalcount, event, nowtime, form)

    group_size += int(form.etunimi0.data and form.sukunimi0.data)
    group_size += int(form.etunimi1.data and form.sukunimi1.data)
    group_size += int(form.etunimi2.data and form.sukunimi2.data)
    group_size += int(form.etunimi3.data and form.sukunimi3.data)

    totalcount += group_size

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and totalcount <= event.get_participant_limit():
        flash('Ilmoittautuminen onnistui')
        sub = _form_to_model(form, group_size, nowtime)
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for('route_pubivisa'))

    elif submitted and totalcount > event.get_participant_limit():
        totalcount -= group_size
        flash('Ilmoittautuminen on jo täynnä')

    elif not validate and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return _render_form(entries, totalcount, event, nowtime, form)


def _render_form(entrys, count, event, nowtime, form):
    return render_template('pubivisa/pubivisa.html',
                           title='pubivisa ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="pubivisa")


def _form_to_model(form, count, nowtime):
    return PubivisaModel(
        teamname=form.teamname.data,
        etunimi0=form.etunimi0.data,
        sukunimi0=form.sukunimi0.data,
        phone0=form.phone0.data,
        email0=form.email0.data,
        kilta0=form.kilta0.data,
        etunimi1=form.etunimi1.data,
        sukunimi1=form.sukunimi1.data,
        phone1=form.phone1.data,
        email1=form.email1.data,
        kilta1=form.kilta1.data,
        etunimi2=form.etunimi2.data,
        sukunimi2=form.sukunimi2.data,
        phone2=form.phone2.data,
        email2=form.email2.data,
        kilta2=form.kilta2.data,
        etunimi3=form.etunimi3.data,
        sukunimi3=form.sukunimi3.data,
        phone3=form.phone3.data,
        email3=form.email3.data,
        kilta3=form.kilta3.data,
        consent0=form.consent0.data,
        consent1=form.consent1.data,
        consent2=form.consent2.data,
        personcount=count,
        datetime=nowtime
    )

def pubivisa_data():
    event = get_event()
    limit = event.get_participant_limit()
    entries = PubivisaModel.query.all()
    count = len(entries)
    return render_template('pubivisa/pubivisa_data.html',
                           title='pubivisa data',
                           entries=entries,
                           count=count,
                           limit=limit)


def pubivisa_csv():
    os.system('mkdir csv')
    sqlite_to_csv.export_to_csv('pubivisa_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='pubivisa_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
