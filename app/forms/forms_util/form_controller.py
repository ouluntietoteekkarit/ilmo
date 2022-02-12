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
    from .form_module_info import ModuleInfo


class FormContext:

    def __init__(self, event: Event, form: Type[FlaskForm], model: Type[db.Model],
                 module_info: ModuleInfo, data_table_info: DataTableInfo):
        self._event = event
        self._form = form
        self._model = model
        self._module_info = module_info
        self._data_table_info = data_table_info

    def get_event(self) -> Event:
        return self._event

    def get_form_type(self) -> Type[FlaskForm]:
        return self._form

    def get_model_type(self) -> Type[db.Model]:
        return self._model

    def get_module_info(self) -> ModuleInfo:
        return self._module_info

    def get_data_table_info(self) -> DataTableInfo:
        return self._data_table_info


class FormController(ABC):

    def __init__(self, context: FormContext):
        self._context = context

    def get_request_handler(self, request) -> Any:
        """
        Render the requested form for this event.
        """
        form = self._context.get_form_type()()
        event = self._context.get_event()
        entries = self._context.get_model_type().query.all()
        return self._render_index_view(entries, event, datetime.now(), form)

    @abstractmethod
    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
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
    def _get_email_recipient(self, form: FlaskForm) -> str:
        pass

    @abstractmethod
    def _get_email_msg(self, form: FlaskForm, reserve: bool) -> str:
        pass

    @abstractmethod
    def _form_to_model(self, form: FlaskForm, nowtime) -> db.Model:
        pass

    def get_data_request_handler(self, request) -> Any:
        return self._render_data_view()

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(self._context.get_model_type().__tablename__)

    def _post_routine(self, form: FlaskForm, model: Type[db.Model]) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = model.query.all()
        count = len(entries)
        maxlimit = event.get_participant_limit() + event.get_participant_reserve()

        if nowtime < event.get_start_time():
            flash('Ilmoittautuminen ei ole alkanut')
            return self._render_index_view(entries, event, nowtime, form)

        if nowtime > event.get_end_time():
            flash('Ilmoittautuminen on päättynyt')
            return self._render_index_view(entries, event, nowtime, form)

        if count >= maxlimit:
            flash('Ilmoittautuminen on jo täynnä')
            return self._render_index_view(entries, event, nowtime, form)

        if self._find_from_entries(entries, form):
            flash('Olet jo ilmoittautunut')
            return self._render_index_view(entries, event, nowtime, form)

        if form.validate_on_submit():
            db.session.add(self._form_to_model(form, nowtime))
            db.session.commit()

            reserve = count >= event.get_participant_limit()
            msg = self._get_email_msg(form, reserve)
            subject = self._context.get_event().get_title()
            flash(_make_success_msg(reserve))
            send_email(msg, subject, self._get_email_recipient(form))

        else:
            flash('Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot')

        return self._render_index_view(entries, event, nowtime, form)

    def _render_index_view(self, entries, event: Event, nowtime, form: FlaskForm, **extra_template_args) -> Any:
        """
        A method to render the index.html template of this event.
        """
        module_info = self._context.get_module_info()
        form_name = module_info.get_form_name()
        return render_template('{}/index.html'.format(form_name), **{
                                   'title': event.get_title(),
                                   'entrys': entries,
                                   'starttime': event.get_start_time(),
                                   'endtime': event.get_end_time(),
                                   'nowtime': nowtime,
                                   'limit': event.get_participant_limit(),
                                   'form': form,
                                   'module_info': module_info,
                                   **extra_template_args})

    def _render_data_view(self) -> Any:
        """
        A helper method to render a data view template.
        """

        module_info = self._context.get_module_info()
        model = self._context.get_model_type()
        event = self._context.get_event()
        table_info = self._context.get_data_table_info()
        limit = event.get_participant_limit()
        entries = model.query.all()
        return render_template('data.html',
                               title='{} data'.format(event.get_title()),
                               entries=entries,
                               count=len(entries),
                               limit=limit,
                               module_info=module_info,
                               table_info=table_info)

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


class DataTableInfo:

    def __init__(self, table_headers, attribute_names):
        self._table_headers = table_headers
        self._attribute_names = attribute_names

    def get_header_names(self):
        return self._table_headers

    def get_attribute_names(self):
        return self._attribute_names
