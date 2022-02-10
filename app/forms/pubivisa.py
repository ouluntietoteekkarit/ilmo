from flask_wtf import FlaskForm
from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, abort
from wtforms import StringField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, length, Required, InputRequired, Optional
from datetime import datetime
import os
from app import db, sqlite_to_csv


class pubivisaForm(FlaskForm):
    teamname = StringField('Joukkueen nimi *', validators=[DataRequired(), length(max=100)])

    etunimi0 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi0 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone0 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email0 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta0 = SelectField('Kilta *', choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
        ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']),
        validators=[DataRequired()])

    etunimi1 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi1 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone1 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email1 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta1 = SelectField('Kilta *', choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
        ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']),
        validators=[DataRequired()])

    etunimi2 = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi2 = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone2 = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email2 = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    kilta2 = SelectField('Kilta *', choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
        ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']),
        validators=[DataRequired()])

    etunimi3 = StringField('Etunimi', validators=[length(max=50)])
    sukunimi3 = StringField('Sukunimi', validators=[length(max=50)])
    phone3 = StringField('Puhelinnumero', validators=[length(max=20)])
    email3 = StringField('Sähköposti', validators=[length(max=100)])
    kilta3 = SelectField('Kilta', choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
        ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']))

    consent0 = BooleanField('Sallin joukkueen nimen julkaisemisen osallistujalistassa')
    consent1 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä *', validators=[DataRequired()])
    consent2 = BooleanField('Ymmärrän, että ilmoittautuminen on sitova *', validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class pubivisaModel(db.Model):
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


def pubivisa_handler(KAPSI):
    form = pubivisaForm()

    starttime = datetime(2020, 10, 7, 12, 00, 00)
    endtime = datetime(2020, 10, 10, 23, 59, 59)
    nowtime = datetime.now()

    limit = 50
    maxlimit = 50
    entrys = pubivisaModel.query.all()
    count = 0
    totalcount = 0
    for entry in entrys:
        totalcount += entry.personcount

    for entry in entrys:
        if (entry.teamname == form.teamname.data):
            flash('Olet jo ilmoittautunut')

            return render_template('pubivisa.html', title='pubivisa ilmoittautuminen',
                                   entrys=entrys,
                                   totalcount=totalcount,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   page="pubivisa")

    if form.etunimi0.data and form.sukunimi0.data:
        count += 1
    if form.etunimi1.data and form.sukunimi1.data:
        count += 1
    if form.etunimi2.data and form.sukunimi2.data:
        count += 1
    if form.etunimi3.data and form.sukunimi3.data:
        count += 1

    totalcount += count

    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()
    else:
        validate = False
        submitted = False

    if validate and submitted and totalcount <= maxlimit:
        flash('Ilmoittautuminen onnistui')
        sub = pubivisaModel(
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
        db.session.add(sub)
        db.session.commit()

        if KAPSI:
            msg = ["echo \"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
                   "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
                   "\n'Joukkueen nimi: ", str(form.teamname.data),
                   "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
                   str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
                   str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
                   str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email0.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

            msg = ["echo \"Hei", str(form.etunimi1.data), str(form.sukunimi1.data),
                   "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
                   "\n'Joukkueen nimi: ", str(form.teamname.data),
                   "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
                   str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
                   str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
                   str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email1.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

            msg = ["echo \"Hei", str(form.etunimi2.data), str(form.sukunimi2.data),
                   "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
                   "\n'Joukkueen nimi: ", str(form.teamname.data),
                   "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
                   str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
                   str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
                   str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email2.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

            msg = ["echo \"Hei", str(form.etunimi3.data), str(form.sukunimi3.data),
                   "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
                   "\n'Joukkueen nimi: ", str(form.teamname.data),
                   "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
                   str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
                   str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
                   str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email3.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

        if KAPSI:
            return redirect('https://ilmo.oty.fi/pubivisa')
        else:
            return redirect(url_for('route_pubivisa'))

    elif submitted and totalcount > maxlimit:
        totalcount -= count
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('pubivisa.html', title='pubivisa ilmoittautuminen',
                           entrys=entrys,
                           totalcount=totalcount,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           page="pubivisa")

def pubivisa_data():
    limit = 50
    entries = pubivisaModel.query.all()
    count = pubivisaModel.query.count()
    return render_template('pubivisa_data.html', title='pubivisa data',
                           entries=entries,
                           count=count,
                           limit=limit)

def pubivisa_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('pubivisa_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='pubivisa_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
