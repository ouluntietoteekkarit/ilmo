from flask_wtf import FlaskForm
from flask import render_template, flash, send_from_directory, abort
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length
from datetime import datetime
import os
from app import db, sqlite_to_csv
from .forms_util.event import Event


class KyselyArvontaJuttuForm(FlaskForm):
    etunimi = StringField('Etunimi *', validators=[DataRequired(), length(max=50)])
    sukunimi = StringField('Sukunimi *', validators=[DataRequired(), length(max=50)])
    email = StringField('Sähköposti *', validators=[DataRequired(), Email(), length(max=100)])
    consent0 = BooleanField('Olen lukenut tietosuojaselosteen ja hyväksyn tietojeni käytön *', validators=[DataRequired()])
    submit = SubmitField('Submit')


class KyselyArvontaJuttuModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))
    consent0 = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime())


def get_event():
    return Event('Hyvinvointi- ja etäopiskelukysely arvonta', datetime(2020, 11, 2, 12, 00, 00), datetime(2020, 11, 23, 23, 59, 59), 4000)


def kysely_arvonta_juttu_handler(request):
    form = KyselyArvontaJuttuForm()
    event = get_event()
    nowtime = datetime.now()
    entries = KyselyArvontaJuttuModel.query.all()
    count = len(entries)

    for entry in entries:
        if (entry.etunimi == form.etunimi.data and entry.sukunimi == form.sukunimi.data) or entry.email == form.email.data:
            flash('Olet jo ilmoittautunut')

            return _render_form(entries, count, event, nowtime, form)

    validate = False
    submitted = False
    if request.method == 'POST':
        validate = form.validate_on_submit()
        submitted = form.is_submitted()

    if validate and submitted and count <= event.get_participant_limit():
        flash('Ilmoittautuminen onnistui')
        sub = _form_to_model(form, nowtime)
        db.session.add(sub)
        db.session.commit()

        # return redirect(url_for('kysely_arvonta_juttu'))
        return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu_redirect.html')

    elif submitted and count > event.get_participant_limit():
        flash('Ilmoittautuminen on jo täynnä')

    elif not validate and submitted:
        flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

    return _render_form(entries, count, event, nowtime, form)


def _render_form(entrys, count, event, nowtime, form):
    return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu.html',
                           title='kysely_arvonta_juttu ilmoittautuminen',
                           entrys=entrys,
                           count=count,
                           starttime=event.get_start_time(),
                           endtime=event.get_end_time(),
                           nowtime=nowtime,
                           limit=event.get_participant_limit(),
                           form=form,
                           page="kysely_arvonta_juttu")


def _form_to_model(form, nowtime):
    return KyselyArvontaJuttuModel(
        etunimi=form.etunimi.data,
        sukunimi=form.sukunimi.data,
        email=form.email.data,
        consent0=form.consent0.data,
        datetime=nowtime,
    )

def kysely_arvonta_juttu_data():
    event = get_event()
    limit = event.get_participant_limit()
    entries = KyselyArvontaJuttuModel.query.all()
    count = len(entries)
    return render_template('kysely_arvonta_juttu/kysely_arvonta_juttu_data.html',
                           title='kysely_arvonta_juttu data',
                           entries=entries,
                           count=count,
                           limit=limit)


def kysely_arvonta_juttu_csv():
    os.system('mkdir csv')
    sqlite_to_csv.export_to_csv('kysely_arvonta_juttu_model')
    dir = os.path.join(os.getcwd(), 'csv/')

    try:
        print(dir)
        return send_from_directory(directory=dir, filename='kysely_arvonta_juttu_model_data.csv', as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
