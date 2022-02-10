from flask_wtf import FlaskForm
from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, abort
from wtforms import StringField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, length, Required, InputRequired, Optional
from .forms import RequiredIf, RequiredIfValue
from datetime import datetime
from app import db, sqlite_to_csv
import os

class korttijalautapeliiltaForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    kilta = SelectField('Kilta *',
                        choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
                                 ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']))

    consent0 = BooleanField('Sallin nimeni julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class korttijalautapeliiltaModel(db.Model):
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


def korttijalautapeliilta_handler(KAPSI):
    form = korttijalautapeliiltaForm()
    starttime = datetime(2020, 10, 7, 12, 00, 00)
    endtime = datetime(2020, 10, 13, 23, 59, 59)
    nowtime = datetime.now()
    limit = 50
    maxlimit = 50
    entrys = korttijalautapeliiltaModel.query.all()
    count = korttijalautapeliiltaModel.query.count()

    for entry in entrys:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data):
            flash('Olet jo ilmoittautunut')

            return render_template('korttijalautapeliilta.html', title='korttijalautapeliilta ilmoittautuminen',
                                   entrys=entrys,
                                   count=count,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   page="korttijalautapeliilta")

    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()
    else:
        validate = False
        submitted = False

    if validate and submitted and count <= maxlimit:
        flash('Ilmoittautuminen onnistui')
        sub = korttijalautapeliiltaModel(
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

        if KAPSI:
            msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                   "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
                   "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                   "\nSähköposti: ", str(form.email.data),
                   "\nPuhelinnumero: ", str(form.phone.data),
                   "\nKilta: ", str(form.kilta.data),
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'kortti- ja lautapeli-ilta ilmoittautuminen' ",
                   str(form.email.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

        if KAPSI:
            return redirect('https://ilmo.oty.fi/korttijalautapeliilta')
        else:
            return redirect(url_for('route_korttijalautapeliilta'))

    elif submitted and count > maxlimit:
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('korttijalautapeliilta.html', title='korttijalautapeliilta ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           page="korttijalautapeliilta")

def korttijalautapeliilta_data():
    limit = 50
    entries = korttijalautapeliiltaModel.query.all()
    count = korttijalautapeliiltaModel.query.count()
    return render_template('korttijalautapeliilta_data.html', title='korttijalautapeliilta data',
                           entries=entries,
                           count=count,
                           limit=limit)

def korttijalautapeliilta_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('korttijalautapeliilta_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='korttijalautapeliilta_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)