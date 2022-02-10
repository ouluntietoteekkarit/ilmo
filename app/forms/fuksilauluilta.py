from flask_wtf import FlaskForm
from flask import Flask, render_template, url_for, redirect, request, flash, send_from_directory, session, abort
from wtforms import StringField, BooleanField, SubmitField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, length, Required, InputRequired, Optional
from datetime import datetime
from app import db, sqlite_to_csv
import os


class fuksilauluiltaForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    consent1 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])

    submit = SubmitField('Ilmoittaudu')


class fuksilauluiltaModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))

    consent1 = db.Column(db.Boolean())

    datetime = db.Column(db.DateTime())

def fuksilauluilta_handler(KAPSI):
    form = fuksilauluiltaForm()
    starttime = datetime(2020, 10, 7, 12, 00, 00)
    endtime = datetime(2020, 10, 13, 23, 59, 59)
    nowtime = datetime.now()
    limit = 70
    maxlimit = 70
    entrys = fuksilauluiltaModel.query.all()
    count = fuksilauluiltaModel.query.count()

    for entry in entrys:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data):
            flash('Olet jo ilmoittautunut')

            return render_template('fuksilauluilta/fuksilauluilta.html', title='fuksilauluilta ilmoittautuminen',
                                   entrys=entrys,
                                   count=count,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   page="fuksilauluilta")

    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()
    else:
        validate = False
        submitted = False

    if validate and submitted and count <= maxlimit:
        flash('Ilmoittautuminen onnistui')
        sub = fuksilauluiltaModel(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            consent1=form.consent1.data,

            datetime=nowtime,
        )
        db.session.add(sub)
        db.session.commit()

        if KAPSI:
            msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                   "\n\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
                   "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                   "\nSähköposti: ", str(form.email.data),
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'fuksilauluilta ilmoittautuminen' ", str(form.email.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

        if KAPSI:
            return redirect('https://ilmo.oty.fi/fuksilauluilta')
        else:
            return redirect(url_for('route_fuksilauluilta'))

    elif submitted and count > maxlimit:
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('fuksilauluilta/fuksilauluilta.html', title='fuksilauluilta ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           page="fuksilauluilta")


def fuksilauluilta_data():
    limit = 70
    entries = fuksilauluiltaModel.query.all()
    count = fuksilauluiltaModel.query.count()
    return render_template('fuksilauluilta/fuksilauluilta_data.html', title='fuksilauluilta data',
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