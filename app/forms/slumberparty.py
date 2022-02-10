from flask_wtf import FlaskForm
from flask import render_template, url_for, redirect, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv


class SlumberpartyForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    phone = StringField('Puhelinnumero *', validators=[DataRequired(), length(max=20)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    kilta = SelectField('Kilta *',
                        choices=(['OTiT', 'OTiT'], ['SIK', 'SIK'], ['YMP', 'YMP'], ['KONE', 'KONE'],
                                 ['PROSE', 'PROSE'], ['OPTIEM', 'OPTIEM'], ['ARK', 'ARK']))

    consent0 = BooleanField('Sallin nimeni julkaisemisen osallistujalistassa')
    consent1 = BooleanField(
        'Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön tapahtuman järjestämisessä *',
        validators=[DataRequired()])
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


def slumberparty_handler(request, kapsi):
    form = SlumberpartyForm()
    starttime = datetime(2020, 10, 21, 12, 00, 00)
    endtime = datetime(2020, 10, 27, 23, 59, 59)
    nowtime = datetime.now()
    limit = 50
    maxlimit = 50
    entrys = SlumberpartyModel.query.all()
    count = SlumberpartyModel.query.count()

    for entry in entrys:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data):
            flash('Olet jo ilmoittautunut')

            return render_template('slumberparty/slumberparty.html', title='slumberparty ilmoittautuminen',
                                   entrys=entrys,
                                   count=count,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   page="slumberparty")

    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()
    else:
        validate = False
        submitted = False

    if validate and submitted and count <= maxlimit:
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

        if kapsi:
            msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                   "\n\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
                   "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                   "\nSähköposti: ", str(form.email.data),
                   "\nPuhelinnumero: ", str(form.phone.data),
                   "\nKilta: ", str(form.kilta.data),
                   "\n\nÄlä vastaa tähän sähköpostiin",
                   "\n\nTerveisin: ropottilari\"",
                   "|mail -aFrom:no-reply@oty.fi -s 'slumberparty ilmoittautuminen' ", str(form.email.data)]

            cmd = ' '.join(msg)
            returned_value = os.system(cmd)

        if kapsi:
            return redirect('https://ilmo.oty.fi/slumberparty')
        else:
            return redirect(url_for('route_slumberparty'))

    elif submitted and count > maxlimit:
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('slumberparty/slumberparty.html', title='slumberparty ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           page="slumberparty")


def slumberparty_data():
    limit = 50
    entries = SlumberpartyModel.query.all()
    count = SlumberpartyModel.query.count()

    return render_template('slumberparty/slumberparty_data.html', title='slumberparty data',
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
