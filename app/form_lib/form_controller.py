from __future__ import annotations
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import send_from_directory, abort, render_template, flash
from typing import Any, Type, TYPE_CHECKING, Iterable, Tuple, List, Dict, Collection
from app import db
from app.sqlite_to_csv import export_to_csv
from app.email import send_email, EmailRecipient
from .lib import Quota

if TYPE_CHECKING:
    from .form_module import ModuleInfo
    from .forms import BasicForm
    from .models import BasicModel


class FormContext:
    """
    A container class for all the static registration form
    information.
    """

    def __init__(self, event: Event, form: Type[BasicForm], model: Type[BasicModel],
                 data_table_info: DataTableInfo):
        self._event = event
        self._form = form
        self._model = model
        self._data_table_info = data_table_info

    def get_event(self) -> Event:
        return self._event

    def get_form_type(self) -> Type[BasicForm]:
        return self._form

    def get_model_type(self) -> Type[BasicModel]:
        return self._model

    def get_data_table_info(self) -> DataTableInfo:
        return self._data_table_info


class EventRegistrations:
    """
    A class to hold dynamic registration data
    """

    def __init__(self, entries: Collection, participant_count: int):
        self._entries = entries
        self._participant_count = participant_count

    def get_entries(self) -> Collection:
        return self._entries

    def get_participant_count(self) -> int:
        return self._participant_count


class FormController(ABC):

    def __init__(self, module_info: ModuleInfo):
        self._module_info = module_info
        self._context = module_info.get_form_context()

    def get_request_handler(self, request) -> Any:
        """
        Render the requested form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        """
        form = self._context.get_form_type()()
        entries = self._context.get_model_type().query.all()
        registrations = EventRegistrations(entries, self._count_participants(entries))
        return self._render_index_view(registrations, form, datetime.now())

    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        Although overriding of this method should be avoided and other
        methods that are used during the post routine should be
        preferred for overriding.
        """
        return self._post_routine(self._context.get_form_type()(), self._context.get_model_type())

    def get_data_request_handler(self, request) -> Any:
        return self._render_data_view()

    def get_data_csv_request_handler(self, request) -> Any:
        return _export_to_csv(self._context.get_model_type().__tablename__)

    def _matching_identity(self, firstname0, firstname1, lastname0, lastname1, email0, email1):
        return firstname0 != '' and lastname0 != '' and email0 != '' and\
            firstname0 == firstname1 and lastname0 == lastname1 and email0 == email1

    def _find_from_entries(self, entries: Iterable[BasicModel], form: BasicForm) -> Tuple[bool, str]:
        """
        A method to find if the individual described by the form is
        found in the entries. Can be overridden in inheriting classes
        to alter behaviour.
        """
        participants = list(form.get_required_participants()) + list(form.get_optional_participants())
        for participant in participants:
            firstname = participant.get_firstname()
            lastname = participant.get_lastname()
            email = participant.get_email()
            for m in entries:
                if self._matching_identity(
                        m.get_firstname(), firstname,
                        m.get_lastname(), lastname,
                        m.get_email(), email):
                    return True, '{} {} on jo ilmoittautunut.'.format(firstname, lastname)

        return False, ''

    def _find_in_self(self, form: BasicForm) -> Tuple[bool, str]:
        """
        Ensure that form itself contains each participant only once.
        """
        participants = list(form.get_required_participants()) + list(form.get_optional_participants())

        length = len(participants) - 1
        for i in range(0, length):
            for j in range(i + 1, length):
                if self._matching_identity(
                        participants[i].get_firstname(), participants[j].get_firstname(),
                        participants[i].get_lastname(), participants[j].get_lastname(),
                        participants[i].get_email(), participants[j].get_email()):
                    return True, 'Et voi ilmoittaa samaa henkilöä kahdesti: {} {}'.format(participants[i].get_firstname(), participants[i].get_lastname())

        return False, ''

    def _count_participants(self, entries: Iterable[BasicModel]) -> int:
        """
        A method to count the number of event participants.
        """
        total_count = 0
        for m in entries:
            total_count += m.get_participant_count()

        return total_count

    def _count_registration_quotas(self, event_quotas: Dict[str, Quota], entries: Collection[BasicModel]) -> Dict[str, int]:
        """
        A method to count the number of event participants per quota.
        """
        registration_quotas = dict.fromkeys(event_quotas.keys(), 0)
        for entry in entries:
            for quota in entry.get_quota_counts():
                registration_quotas[quota.get_name()] += quota.get_quota()

        return registration_quotas

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

    def _form_to_model(self, form: BasicForm, nowtime: datetime) -> BasicModel:
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
            reserve = registrations.get_participant_count() + model.get_participant_count() >= event.get_participant_limit()
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
        """
        Checks that the submitted form is correctly filled
        and that all registration conditions are met.
        Can be overridden in inheriting classes to alter behaviour.
        Overriding methods should call this method first.

        Empty string is returned if everything checks.
        """
        event = self._context.get_event()

        if not self._validate_form(form):
            return 'Ilmoittautuminen epäonnistui, tarkista syöttämäsi tiedot'

        if nowtime < event.get_start_time():
            return 'Ilmoittautuminen ei ole alkanut'

        if nowtime > event.get_end_time():
            return 'Ilmoittautuminen on päättynyt'

        msg = self._check_quotas(event.get_quotas(), registrations, form.get_quota_counts())
        if len(msg) != 0:
            return msg

        (found, msg) = self._find_from_entries(registrations.get_entries(), form)
        if found:
            return msg or 'Olet jo ilmoittautunut'

        (found, msg) = self._find_in_self(form)
        if found:
            return msg

        return ""

    def _validate_form(self, form: BasicForm) -> bool:
        valid = form.get_required_participants().validate(form)
        valid = form.get_other_attributes().validate() and valid
        for participant in form.get_optional_participants():
            for field in participant:
                if field.raw_data:
                    valid = participant.validate() and valid
                    break

        return valid

    def _check_quotas(self, event_quotas: Dict[str, Quota],
                      registrations: EventRegistrations, form_quotas: Iterable[Quota]) -> str:
        """
        Ensure that no quota has been exceeded
        """
        registration_quotas = self._count_registration_quotas(event_quotas, registrations.get_entries())
        for form_quota in form_quotas:
            name = form_quota.get_name()
            registration_quotas[name] += form_quota.get_quota()
            if registration_quotas[name] > event_quotas[name].get_max_quota():
                if name != Quota.default_quota_name():
                    return 'Ilmoittautuminen on jo täynnä kiintiön {} osalta'.format(name)
                return 'Ilmoittautuminen on jo täynnä'

        return ''

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

    def _render_index_view(self, registrations: EventRegistrations,
                           form: BasicForm, nowtime, **extra_template_args) -> Any:
        """
        A method to render the index.html template of this event.
        """
        module_info = self._module_info
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
        model = self._context.get_model_type()
        entries = model.query.all()
        registrations = EventRegistrations(entries, self._count_participants(entries))
        return render_template('data.html',
                               event=self._context.get_event(),
                               registrations=registrations,
                               module_info=self._module_info,
                               table_info=self._context.get_data_table_info())


def _make_success_msg(reserve: bool) -> str:
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

    def __init__(self, title: str, start_time: datetime,
                 end_time: datetime, quotas: Iterable[Quota],
                 list_participant_names: bool):
        self._title = title
        self._start_time = start_time
        self._end_time = end_time
        self._list_participant_names = list_participant_names
        self._participant_limit = 0
        self._max_participant_limit = 0
        self._quotas = {}
        for quota in quotas:
            self._quotas[quota.get_name()] = quota
            self._participant_limit += quota.get_quota()
            self._max_participant_limit += quota.get_max_quota()

    def get_title(self) -> str:
        return self._title

    def get_start_time(self) -> datetime:
        return self._start_time

    def get_end_time(self) -> datetime:
        return self._end_time

    def get_quotas(self) -> Dict[str, Quota]:
        return self._quotas

    def get_participant_limit(self) -> int:
        return self._participant_limit

    def get_max_limit(self) -> int:
        return self._max_participant_limit

    def get_list_participant_name(self) -> bool:
        return self._list_participant_names



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
