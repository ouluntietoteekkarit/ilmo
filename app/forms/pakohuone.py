from flask_wtf import FlaskForm
from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, abort
from wtforms import StringField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, length, Required, InputRequired, Optional
from .forms import RequiredIf, RequiredIfValue
from datetime import datetime
from app import db, sqlite_to_csv
import os
import json

class pakohuoneForm(FlaskForm):
    aika = RadioField('Aika *',
                      choices=(['18:00', '18:00'], ['19:30', '19:30']),
                      validators=[DataRequired()])

    huone1800 = RadioField('Huone (18:00) *',
                           choices=(['Pommi (Uusikatu)', ''],
                                    ['Kuolleen miehen saari (Uusikatu)', ''],
                                    ['Temppelin kirous (Uusikatu)', ''],
                                    ['Velhon perintö (Uusikatu)', ''],
                                    ['Murhamysteeri (Kajaaninkatu)', ''],
                                    ['Vankilapako (Kajaaninkatu)', ''],
                                    ['Professorin arvoitus (Kajaaninkatu)', ''],
                                    ['The SAW (Kirkkokatu)', ''],
                                    ['Alcatraz (Kirkkokatu)', ''],
                                    ['Matka maailman ympäri (Kirkkokatu)', ''],
                                    ['', '']),
                           validators=[RequiredIfValue(other_field_name='aika', value='18:00')],
                           default=(['', '']))

    huone1930 = RadioField('Huone (19:30) *',
                           choices=(['Pommi (Uusikatu)', ''],
                                    ['Kuolleen miehen saari (Uusikatu)', ''],
                                    ['Temppelin kirous (Uusikatu)', ''],
                                    ['Velhon perintö (Uusikatu)', ''],
                                    ['Murhamysteeri (Kajaaninkatu)', ''],
                                    ['Vankilapako (Kajaaninkatu)', ''],
                                    ['Professorin arvoitus (Kajaaninkatu)', ''],
                                    ['The SAW (Kirkkokatu)', ''],
                                    ['Alcatraz (Kirkkokatu)', ''],
                                    ['Matka maailman ympäri (Kirkkokatu)', ''],
                                    ['', '']),
                           validators=[RequiredIfValue(other_field_name='aika', value='19:30')],
                           default=(['', '']))

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


class pakohuoneModel(db.Model):
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


def pakohuone_handler(KAPSI):
    starttime = datetime(2020, 11, 5, 12, 00, 00)
    endtime = datetime(2020, 11, 9, 23, 59, 59)
    nowtime = datetime.now()

    limit = 20
    maxlimit = 20

    entrys = pakohuoneModel.query.all()
    count = pakohuoneModel.query.count()

    varatut = []
    for entry in entrys:
        varatut.append((entry.aika, entry.huone1800, entry.huone1930))

    form = pakohuoneForm()

    for entry in entrys:
        if ((entry.etunimi0 == form.etunimi0.data and entry.sukunimi0 == form.sukunimi0.data) or entry.email0 == form.email0.data):
            flash('Olet jo ilmoittautunut')

            return render_template('pakohuone.html', title='pakohuone ilmoittautuminen',
                                   entrys=entrys,
                                   count=count,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   varatut=json.dumps(varatut),
                                   page="pakohuone")

    for entry in entrys:
        if (entry.aika == form.aika.data):
            if (entry.aika == "18:00"):
                if (entry.huone1800 == form.huone1800.data):
                    flash('Valisemasi huone on jo varattu valitsemanasi aikana')

                    return render_template('pakohuone.html', title='pakohuone ilmoittautuminen',
                                           entrys=entrys,
                                           count=count,
                                           starttime=starttime,
                                           endtime=endtime,
                                           nowtime=nowtime,
                                           limit=limit,
                                           form=form,
                                           varatut=json.dumps(varatut),
                                           page="pakohuone")

            elif (entry.aika == "19:30"):
                if (entry.huone1930 == form.huone1930.data):
                    flash('Valisemasi huone on jo varattu valitsemanasi aikana')

                    return render_template('pakohuone.html', title='pakohuone ilmoittautuminen',
                                           entrys=entrys,
                                           count=count,
                                           starttime=starttime,
                                           endtime=endtime,
                                           nowtime=nowtime,
                                           limit=limit,
                                           form=form,
                                           varatut=json.dumps(varatut),
                                           page="pakohuone")

    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()
    else:
        validate = False
        submitted = False

    if validate and submitted and count <= maxlimit:
        flash('Ilmoittautuminen onnistui')
        sub = pakohuoneModel(
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

        if KAPSI:
            msg = ["echo \"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
                   "\n\nOlet ilmoittautunut OTYn Pakopelipäivä tapahtumaan. Syötit seuraavia tietoja: ",
                   "\n'Nimi: ", str(form.etunimi0.data), str(form.sukunimi0.data),
                   "\nSähköposti: ", str(form.email0.data),
                   "\nPuhelinnumero: ", str(form.phone0.data),
                   "\nMuiden joukkuelaisten nimet: ", str(form.etunimi1.data), str(form.sukunimi1.data),
                   str(form.etunimi2.data), str(form.sukunimi2.data),
                   str(form.etunimi3.data), str(form.sukunimi3.data),
                   str(form.etunimi4.data), str(form.sukunimi4.data),
                   str(form.etunimi5.data), str(form.sukunimi5.data),
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'pakopelipäivä ilmoittautuminen' ", str(form.email0.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

        if KAPSI:
            return redirect('https://ilmo.oty.fi/pakohuone')
        else:
            return redirect(url_for('route_pakohuone'))

    elif submitted and count > maxlimit:
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('pakohuone.html', title='pakohuone ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           varatut=json.dumps(varatut),
                           page="pakohuone")


def pakohuone_data():
    limit = 20
    entries = pakohuoneModel.query.all()
    count = pakohuoneModel.query.count()

    return render_template('pakohuone_data.html', title='pakohuone data',
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