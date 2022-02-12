from __future__ import annotations
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import send_from_directory, abort, render_template, flash
from typing import Any, Type, TYPE_CHECKING
from app import db
from app.sqlite_to_csv import export_to_csv
from app.email import send_email

if TYPE_CHECKING:
    from flask_wtf import FlaskForm
    from .event import Event
    from .forms import DataTableInfo
    from .form_module_info import ModuleInfo


class FormController(ABC):

    @abstractmethod
    def get_request_handler(self, request) -> Any:
        """
        Render the requested form for this event.
        """
        pass

    @abstractmethod
    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
        """
        pass

    @abstractmethod
    def get_data_request_handler(self, request) -> Any:
        """
        Handle data view for this event.
        """
        pass

    @abstractmethod
    def get_data_csv_request_handler(self, request) -> Any:
        """
        Handle data download as CSV
        """
        pass

    @abstractmethod
    def _get_event(self) -> Event:
        """
        Return event object containing this event's information
        """
        pass

    @abstractmethod
    def _render_form(self, entries, count: int, event: Event, nowtime, form: FlaskForm) -> Any:
        """
        A method to render the index.html template of this event.
        """
        pass

    @abstractmethod
    def _find_from_entries(self, entries, form: FlaskForm) -> bool:
        """
        A method to find if the individual described by the form is
        found in the entries
        """
        pass

    @abstractmethod
    def _get_email_subject(self) -> str:
        pass

    @abstractmethod
    def _get_email_recipient(self, form: FlaskForm) -> str:
        pass

    @abstractmethod
    def _get_email_msg(self, form: FlaskForm, reserve: bool) -> str:
        pass

    @abstractmethod
    def _form_to_model(self, form: FlaskForm, nowtime) -> db.Model:
        pass

    @abstractmethod
    def _get_data_table_info(self) -> DataTableInfo:
        pass

    def _post_routine(self, form: FlaskForm, model: Type[db.Model]) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        event = self._get_event()
        nowtime = datetime.now()
        entries = model.query.all()
        count = len(entries)
        maxlimit = event.get_participant_limit() + event.get_participant_reserve()

        if nowtime < event.get_start_time():
            flash('Ilmoittautuminen ei ole alkanut')
            return self._render_form(entries, count, event, nowtime, form)

        if nowtime > event.get_end_time():
            flash('Ilmoittautuminen on päättynyt')
            return self._render_form(entries, count, event, nowtime, form)

        if count >= maxlimit:
            flash('Ilmoittautuminen on jo täynnä')
            return self._render_form(entries, count, event, nowtime, form)

        if self._find_from_entries(entries, form):
            flash('Olet jo ilmoittautunut')
            return self._render_form(entries, count, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(self._form_to_model(form, nowtime))
            db.session.commit()

            reserve = count >= event.get_participant_limit()
            msg = self._get_email_msg(form, reserve)
            flash(_make_success_msg(reserve))
            send_email(msg, self._get_email_subject(), self._get_email_recipient(form))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return self._render_form(entries, count, event, nowtime, form)

    def _data_view(self, form_info: ModuleInfo, model, **additional_template_args) -> Any:
        """
        A helper method to render a data view template.
        """
        event = self._get_event()
        table_info = self._get_data_table_info()
        limit = event.get_participant_limit()
        entries = model.query.all()
        count = len(entries)
        return render_template('data.html', **{
            'title': '{} data'.format(event.get_name()),
            'entries': entries,
            'count': count,
            'limit': limit,
            'form_info': form_info,
            'table_info': table_info,
            **additional_template_args
        })

    def _export_to_csv(self, table_name: str) -> Any:
        """
        A method to export and send out the event's registration data as a CSV file
        """
        os.system('mkdir csv')
        csv_path = export_to_csv(table_name)
        (folder, file) = os.path.split(csv_path)
        try:
            return send_from_directory(directory=folder, filename=file, as_attachment=True)
        except FileNotFoundError as e:
            print(e)
            abort(404)


def _make_success_msg(reserve: bool):
    if reserve:
        return 'Ilmoittautuminen onnistui, olet varasijalla'
    else:
        return 'Ilmoittautuminen onnistui'
