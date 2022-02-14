from __future__ import annotations
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import send_from_directory, abort, render_template, flash
from typing import Any, Type, TYPE_CHECKING, Iterable, Tuple, List
from app import db
from app.sqlite_to_csv import export_to_csv
from app.email import send_email, EmailRecipient
from .forms import BasicForm
from .models import BasicModel

if TYPE_CHECKING:
    from .form_module import ModuleInfo


class FormContext:
    """
    A container class for all the static registration form
    information.
    """

    def __init__(self, event: Event, form: Type[BasicForm], model: Type[BasicModel],
                 module_info: ModuleInfo, data_table_info: DataTableInfo):
        self._event = event
        self._form = form
        self._model = model
        self._module_info = module_info
        self._data_table_info = data_table_info

    def get_event(self) -> Event:
        return self._event

    def get_form_type(self) -> Type[Type[BasicForm]]:
        return self._form

    def get_model_type(self) -> Type[BasicModel]:
        return self._model

    def get_module_info(self) -> ModuleInfo:
        return self._module_info

    def get_data_table_info(self) -> DataTableInfo:
        return self._data_table_info


class EventRegistrations:
    """
    A class to hold dynamic registration data
    """

    def __init__(self, entries, participant_count: int):
        self._entries = entries
        self._participant_count = participant_count

    def get_entries(self):
        return self._entries

    def get_participant_count(self):
        return self._participant_count


class FormController(ABC):

    def __init__(self, event: Event, form: Type[BasicForm], model: Type[BasicModel],
                 module_info: ModuleInfo, data_table_info: DataTableInfo):
        self._context = FormContext(event, form, model, module_info, data_table_info)

    def get_request_handler(self, request) -> Any:
        """
        Render the requested form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        """
        form = self._context.get_form_type()()
        event = self._context.get_event()
        entries = self._context.get_model_type().query.all()
        registrations = EventRegistrations(entries, self._count_participants(entries))
        return self._render_index_view(registrations, form, datetime.now())

    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        """
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    def get_data_request_handler(self, request) -> Any:
        return self._render_data_view()

    def get_data_csv_request_handler(self, request) -> Any:
        return _export_to_csv(self._context.get_model_type().__tablename__)

    def _find_from_entries(self, entries: Iterable[BasicModel], form: BasicForm) -> bool:
        """
        A method to find if the individual described by the form is
        found in the entries. Can be overridden in inheriting classes
        to alter behaviour.
        """
        firstname = form.get_firstname()
        lastname = form.get_lastname()
        email = form.get_email()
        for entry in entries:
            if (entry.get_firstname() == firstname and entry.get_lastname() == lastname) or entry.get_email() == email:
                return True
        return False

    def _count_participants(self, entries) -> int:
        """
        A method to count the number of event participants.
        Can be overridden in inheriting classes to alter behaviour.
        """
        return len(entries)

    def _get_email_recipient(self, model: BasicModel) -> List[EmailRecipient]:
        """
        A method to get all email recipients to whom an email
        concerning current registration should be sent to.
         Can be overridden in inheriting classes to alter behaviour.
        """
        return [
            EmailRecipient(model.get_firstname(), model.get_lastname(), model.get_email())
        ]

    @abstractmethod
    def _get_email_msg(self, recipient: EmailRecipient, model: BasicModel, reserve: bool) -> str:
        pass

    def _form_to_model(self, form: BasicForm, nowtime) -> BasicModel:
        """
        A method to convert form into a model.
        Can be overridden in inheriting classes to alter behaviour.
        """
        model = self._context.get_model_type()(datetime=nowtime)
        form.populate_obj(model)
        return model

    def _post_routine(self, form: BasicForm, model: Type[BasicModel]) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        event = self._context.get_event()
        nowtime = datetime.now()
        entries = model.query.all()
        registrations = EventRegistrations(entries, self._count_participants(entries))

        error_msg = self._check_form_submit(registrations, form, nowtime)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(registrations, form, nowtime)

        model = self._form_to_model(form, nowtime)
        if self._insert_model(model):
            reserve = registrations.get_participant_count() >= event.get_participant_limit()
            flash(_make_success_msg(reserve))
            self._send_emails(model, reserve)

        return self._post_routine_output(registrations, form, nowtime)

    def _post_routine_output(self, registrations, form: BasicForm, nowtime) -> Any:
        """
        A method that handles post request output rendering.
        Can be overridden in inheriting classes to alter behaviour.
        """
        return self._render_index_view(registrations, form, nowtime)

    def _check_form_submit(self, registrations: EventRegistrations, form: BasicForm, nowtime) -> str:
        event = self._context.get_event()

        if not form.validate_on_submit():
            return 'Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot'

        if nowtime < event.get_start_time():
            return 'Ilmoittautuminen ei ole alkanut'

        if nowtime > event.get_end_time():
            return 'Ilmoittautuminen on päättynyt'

        if registrations.get_participant_count() >= event.get_max_limit():
            return 'Ilmoittautuminen on jo täynnä'

        if self._find_from_entries(registrations.get_entries(), form):
            return 'Olet jo ilmoittautunut'

        return ""

    def _insert_model(self, model: BasicModel) -> bool:
        try:
            db.session.add(model)
            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            flash('Tietokanta virhe. Yritä uudestaan.')
            print(e)

        return False

    def _send_emails(self, model: BasicModel, reserve: bool) -> None:
        subject = self._context.get_event().get_title()
        for recipient in self._get_email_recipient(model):
            msg = self._get_email_msg(recipient, model, reserve)
            send_email(msg, subject, recipient)

    def _render_index_view(self, registrations: EventRegistrations, form: BasicForm, nowtime, **extra_template_args) -> Any:
        """
        A method to render the index.html template of this event.
        """
        module_info = self._context.get_module_info()
        form_name = module_info.get_form_name()
        return render_template('{}/index.html'.format(form_name), **{
                                   'registrations': registrations,
                                   'event': self._context.get_event(),
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


def _make_success_msg(reserve: bool):
    if reserve:
        return 'Ilmoittautuminen onnistui, olet varasijalla'
    else:
        return 'Ilmoittautuminen onnistui'


class DataTableInfo:
    """
    Class to contain database model attribute mapping
    when exporting the data as CSV.
    """

    def __init__(self, table_structure: Iterable[Tuple[str, str]]):
        (self._attribute_names, self._table_headers) = list(zip(*table_structure))

    def get_header_names(self) -> List:
        return self._table_headers

    def get_attribute_names(self) -> List:
        return self._attribute_names


class Event(object):
    """
    A readonly class containing event's information.
    """

    def __init__(self, title: str, start_time, end_time, participant_limit: int, participant_reserve: int, list_participant_name: bool):
        self.title = title
        self._start_time = start_time
        self._end_time = end_time
        self._participant_limit = participant_limit
        self._participant_reserve = participant_reserve
        self._list_paticipant_names = list_participant_name

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

    def get_list_participant_name(self) -> bool:
        return self._list_paticipant_names

    def get_max_limit(self) -> int:
        return self._participant_limit + self._participant_reserve


def _export_to_csv(table_name: str) -> Any:
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
