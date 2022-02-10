from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
import json
from app import db, sqlite_to_csv
from .forms_util.forms import RequiredIfValue
from .forms_util.event import Event


def get_escape_games():
    return [
       'Pommi (Uusikatu)',
       'Kuolleen miehen saari (Uusikatu)',
       'Temppelin kirous (Uusikatu)',
       'Velhon perintö (Uusikatu)',
       'Murhamysteeri (Kajaaninkatu)',
       'Vankilapako (Kajaaninkatu)',
       'Professorin arvoitus (Kajaaninkatu)',
       'The SAW (Kirkkokatu)',
       'Alcatraz (Kirkkokatu)',
       'Matka maailman ympäri (Kirkkokatu)',
    ]


def get_game_choices():
    choices = []
    for game in get_escape_games():
        choices.append((game, game))
    return choices


class PakohuoneForm(FlaskForm):
    aika = RadioField('Aika *', choices=[('18:00', '18:00'), ('19:30', '19:30')], validators=[DataRequired()])
    huone1800 = RadioField('Huone (18:00) *', choices=get_game_choices(), validators=[RequiredIfValue(other_field_name='aika', value='18:00')])
    huone1930 = RadioField('Huone (19:30) *', choices=get_game_choices(), validators=[RequiredIfValue(other_field_name='aika', value='19:30')])

    etunimi0 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi0 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email0 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi3 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi3 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi4 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi4 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])

    etunimi5 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi5 = StringField('Sukunimi', validators=[length(max=50)])

    consent0 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class PakohuoneModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    aika = db.Column(db.String(16))
    huone1800 = db.Column(db.String(128))
    huone1930 = db.Column(db.String(128))

    etunimi0 = db.Column(db.String(64))
    sukunimi0 = db.Column(db.String(64))
    phone0 = db.Column(db.String(32))
    email0 = db.Column(db.String(128))

    etunimi1 = db.Column(db.String(64))
    sukunimi1 = db.Column(db.String(64))

    etunimi2 = db.Column(db.String(64))
    sukunimi2 = db.Column(db.String(64))

    etunimi3 = db.Column(db.String(64))
    sukunimi3 = db.Column(db.String(64))

    etunimi4 = db.Column(db.String(64))
    sukunimi4 = db.Column(db.String(64))

    etunimi5 = db.Column(db.String(64))
    sukunimi5 = db.Column(db.String(64))

    consent0 = db.Column(db.Boolean())

    datetime = db.Column(db.DateTime())


def pakohuone_handler(request):
    form = PakohuoneForm()
    event = Event('Pakohuone', datetime(2020, 11, 5, 12, 00, 00), datetime(2020, 11, 9, 23, 59, 59), 20)
    nowtime = datetime.now()
    entrys = PakohuoneModel.query.all()
    count = PakohuoneModel.query.count()

    varatut = []
    for entry in entrys:
        varatut.append((entry.aika, entry.huone1800, entry.huone1930))

    for entry in entrys:
        if (entry.etunimi0 == form.etunimi0.data and entry.sukunimi0 == form.sukunimi0.data) or entry.email0 == form.email0.data:
            flash('Olet jo ilmoittautunut')

            return render_form(entrys, count, event, nowtime, form, varatut)

    for entry in entrys:
        if entry.aika == form.aika.data:
            if (entry.aika == "18:00" and entry.huone1800 == form.huone1800.data) or (entry.aika == "19:30" and entry.huone1930 == form.huone1930.data):
                flash('Valisemasi huone on jo varattu valitsemanasi aikana')
                return render_form(entrys, count, event, nowtime, form, varatut)

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and count <= event.get_participant_limit():
        flash('Ilmoittautuminen onnistui')
        sub = PakohuoneModel(
            aika=form.aika.data,
            huone1800=form.huone1800.data,
            huone1930=form.huone1930.data,
            etunimi0=form.etunimi0.data,
            sukunimi0=form.sukunimi0.data,
            phone0=form.phone0.data,
            email0=form.email0.data,
            etunimi1=form.etunimi1.data,
            sukunimi1=form.sukunimi1.data,
            etunimi2=form.etunimi2.data,
            sukunimi2=form.sukunimi2.data,
            etunimi3=form.etunimi3.data,
            sukunimi3=form.sukunimi3.data,
            etunimi4=form.etunimi4.data,
            sukunimi4=form.sukunimi4.data,
            etunimi5=form.etunimi5.data,
            sukunimi5=form.sukunimi5.data,
            consent0=form.consent0.data,
            datetime=nowtime
        )
        db.session.add(sub)
        db.session.commit()

        return redirect(url_for('route_pakohuone'))

    elif submitted and count > event.get_participant_limit():
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_form(entrys, count, event, nowtime, form, varatut)


def render_form(entrys, count, event, nowtime, form, varatut):
    return render_template('pakohuone/pakohuone.html',
                           title='pakohuone ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           varatut=json.dumps(varatut),
                           page="pakohuone")

def pakohuone_data():
    limit = 20
    entries = PakohuoneModel.query.all()
    count = PakohuoneModel.query.count()

    return render_template('pakohuone/pakohuone_data.html',
                           title='pakohuone data',
                           entries=entries,
                           count=count,
                           limit=limit)


def pakohuone_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('pakohuone_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='pakohuone_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
