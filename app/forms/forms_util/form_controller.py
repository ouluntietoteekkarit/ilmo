from __future__ import annotations
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import send_from_directory, abort, render_template, flash
from typing import Any, Type, TYPE_CHECKING, Iterable, Tuple
from app import db
from app.sqlite_to_csv import export_to_csv
from app.email import send_email
from .forms import basic_form
from .models import BasicModel

if TYPE_CHECKING:
    from .form_module_info import ModuleInfo


class FormContext:

    def __init__(self, event: Event, form: Type[basic_form()], model: Type[BasicModel],
                 module_info: ModuleInfo, data_table_info: DataTableInfo):
        self._event = event
        self._form = form
        self._model = model
        self._module_info = module_info
        self._data_table_info = data_table_info

    def get_event(self) -> Event:
        return self._event

    def get_form_type(self) -> Type[Type[basic_form()]]:
        return self._form

    def get_model_type(self) -> Type[BasicModel]:
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
        Can be overridden in inheriting class to alter the behaviour.
        """
        form = self._context.get_form_type()()
        event = self._context.get_event()
        entries = self._context.get_model_type().query.all()
        return self._render_index_view(entries, event, datetime.now(), form)

    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        """
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    @abstractmethod
    def _find_from_entries(self, entries, form: Type[basic_form()]) -> bool:
        """
        A method to find if the individual described by the form is
        found in the entries
        """
        pass

    @abstractmethod
    def _get_email_recipient(self, form: Type[basic_form()]) -> str:
        pass

    @abstractmethod
    def _get_email_msg(self, form: Type[basic_form()], reserve: bool) -> str:
        pass

    def _form_to_model(self, form: Type[basic_form()], nowtime) -> BasicModel:
        """
        A method to convert form into a model.
        Can be overridden in inheriting classes to alter behaviour.
        """
        model = self._context.get_model_type()(datetime=nowtime)
        form.populate_obj(model)
        return model

    def get_data_request_handler(self, request) -> Any:
        return self._render_data_view()

    def get_data_csv_request_handler(self, request) -> Any:
        return self._export_to_csv(self._context.get_model_type().__tablename__)

    def _post_routine(self, form: Type[basic_form()], model: Type[BasicModel]) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = model.query.all()
        count = len(entries)

        error_msg = self._check_form_submit(event, form, entries, nowtime, count)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(entries, event, nowtime, form)

        if self._insert_model(form, nowtime):
            reserve = count >= event.get_participant_limit()
            msg = self._get_email_msg(form, reserve)
            subject = self._context.get_event().get_title()
            flash(_make_success_msg(reserve))
            send_email(msg, subject, self._get_email_recipient(form))

        return self._render_index_view(entries, event, nowtime, form)

    def _check_form_submit(self, event: Event, form: Type[basic_form()], entries,
                           nowtime, participant_count: int) -> str:

        if not form.validate_on_submit():
            return 'Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot'

        if nowtime < event.get_start_time():
            return 'Ilmoittautuminen ei ole alkanut'

        if nowtime > event.get_end_time():
            return 'Ilmoittautuminen on päättynyt'

        if participant_count >= event.get_max_limit():
            return 'Ilmoittautuminen on jo täynnä'

        if self._find_from_entries(entries, form):
            return 'Olet jo ilmoittautunut'

        return ""

    def _insert_model(self, form: Type[basic_form()], nowtime) -> bool:
        try:
            db.session.add(self._form_to_model(form, nowtime))
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            flash('Tietokanta virhe. Yritä uudestaan.')
            print(e)

        return False

    def _render_index_view(self, entries, event: Event, nowtime, form: basic_form(), **extra_template_args) -> Any:
        """
        A method to render the index.html template of this event.
        """
        module_info = self._context.get_module_info()
        form_name = module_info.get_form_name()
        return render_template('{}/index.html'.format(form_name), **{
                                   'entries': entries,
                                   'event': event,
                                   'nowtime': nowtime,
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

    def __init__(self, table_structure: Iterable[Tuple[str, str]]):
        (self._attribute_names, self._table_headers) = list(zip(*table_structure))

    def get_header_names(self):
        return self._table_headers

    def get_attribute_names(self):
        return self._attribute_names


class Event(object):

    def __init__(self, title: str, start_time, end_time, participant_limit: int, participant_reserve: int):
        self.title = title
        self._start_time = start_time
        self._end_time = end_time
        self._participant_limit = participant_limit
        self._participant_reserve = participant_reserve

    def get_title(self) -> str:
        return self.title

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time

    def get_participant_limit(self) -> int:
        return self._participant_limit

    def get_participant_reserve(self) -> int:
        return self._participant_reserve

    def get_max_limit(self) -> int:
        return self._participant_limit + self._participant_reserve
