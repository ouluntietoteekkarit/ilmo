from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv
from .forms_util.guilds import *
from .forms_util.event import Event


def get_guilds():
    return [
        Guild(GUILD_OTIT),
        Guild(GUILD_SIK),
        Guild(GUILD_YMP),
        Guild(GUILD_KONE),
        Guild(GUILD_PROSE),
        Guild(GUILD_OPTIEM),
        Guild(GUILD_ARK)
    ]


def get_guild_choices():
    choices = []
    for guild in get_guilds():
        choices.append((guild.get_name(), guild.get_name()))
    return choices

class SlumberpartyForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta = SelectField('Kilta *', choices=get_guild_choices())
    consent0 = BooleanField('Sallin nimeni julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])
    submit = SubmitField('Ilmoittaudu')


class SlumberpartyModel(db.Model):
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


def slumberparty_handler(request):
    form = SlumberpartyForm()
    event = Event('Slumberparty', datetime(2020, 10, 21, 12, 00, 00), datetime(2020, 10, 27, 23, 59, 59), 50)
    nowtime = datetime.now()
    entrys = SlumberpartyModel.query.all()
    count = SlumberpartyModel.query.count()

    for entry in entrys:
        if entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data:
            flash('Olet jo ilmoittautunut')
            return render_form(entrys, count, event, nowtime, form)

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and count <= event.get_participant_limit():
        flash('Ilmoittautuminen onnistui')
        sub = SlumberpartyModel(
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
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for('route_slumberparty'))

    elif submitted and count > event.get_participant_limit():
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_form(entrys, count, event, nowtime, form)


def render_form(entrys, count, event, nowtime, form):
    return render_template('slumberparty/slumberparty.html',
                           title='slumberparty ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="slumberparty")


def slumberparty_data():
    limit = 50
    entries = SlumberpartyModel.query.all()
    count = SlumberpartyModel.query.count()

    return render_template('slumberparty/slumberparty_data.html',
                           title='slumberparty data',
                           entries=entries,
                           count=count,
                           limit=limit)


def slumberparty_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('slumberparty_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='slumberparty_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
