from flask_wtf import FlaskForm
from flask import render_template, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv


class KyselyArvontaJuttuForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])

    consent0 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön *',
                            validators=[DataRequired()])

    submit = SubmitField('Submit')


class KyselyArvontaJuttuModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent0 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


def kysely_arvonta_juttu_handler(request):
    form = KyselyArvontaJuttuForm()
    starttime = datetime(2020, 11, 2, 12, 00, 00)
    endtime = datetime(2020, 11, 23, 23, 59, 59)
    nowtime = datetime.now()
    limit = 4000
    maxlimit = 4000
    entrys = KyselyArvontaJuttuModel.query.all()
    count = KyselyArvontaJuttuModel.query.count()

    for entry in entrys:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data) or entry.email == form.email.data:
            flash('Olet jo ilmoittautunut')

            return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu.html',
                                   title='kysely_arvonta_juttu ilmoittautuminen',
                                   entrys=entrys,
                                   count=count,
                                   starttime=starttime,
                                   endtime=endtime,
                                   nowtime=nowtime,
                                   limit=limit,
                                   form=form,
                                   page="kysely_arvonta_juttu")

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and count <= maxlimit:
        flash('Ilmoittautuminen onnistui')
        sub = KyselyArvontaJuttuModel(
            etunimi=form.etunimi.data,
            sukunimi=form.sukunimi.data,
            email=form.email.data,
            consent0=form.consent0.data,
            datetime=nowtime,
        )
        db.session.add(sub)
        db.session.commit()

        # return redirect(url_for('kysely_arvonta_juttu'))
        return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu_redirect.html')

    elif submitted and count > maxlimit:
        flash('Ilmoittautuminen on jo täynnä')

    elif (not validate) and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu.html',
                           title='kysely_arvonta_juttu ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=starttime,
                           endtime=endtime,
                           nowtime=nowtime,
                           limit=limit,
                           form=form,
                           page="kysely_arvonta_juttu")


def kysely_arvonta_juttu_data():
    limit = 4000
    entries = KyselyArvontaJuttuModel.query.all()
    count = KyselyArvontaJuttuModel.query.count()

    return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu_data.html',
                           title='kysely_arvonta_juttu data',
                           entries=entries,
                           count=count,
                           limit=limit)


def kysely_arvonta_juttu_csv():
    os.system('mkdir csv')
    sqlite_to_csv.exportToCSV('kysely_arvonta_juttu_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='kysely_arvonta_juttu_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
