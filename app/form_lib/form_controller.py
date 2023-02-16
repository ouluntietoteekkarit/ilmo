from __future__ import annotations

import copy
import os
from abc import ABC, abstractmethod
from datetime import datetime
from flask import send_from_directory, abort, render_template, flash
from typing import Any, Type, TYPE_CHECKING, Iterable, Tuple, Dict, Collection
from app import db
from app.sqlite_to_csv import export_to_csv
from app.email import send_email, EmailRecipient
from .event import Event
from .eventregistrations import EventRegistrations
from .lib import BaseParticipant
from .quota import Quota

if TYPE_CHECKING:
    from .form_module import ModuleInfo
    from .forms import RegistrationForm
    from .models import RegistrationModel


class FormContext:
    """
    A container class for all the static registration form
    information.
    """

    def __init__(self, event: Event, form: Type[RegistrationForm], model: Type[RegistrationModel],
                 data_table_info: DataTableInfo):
        self._event = event
        self._form = form
        self._model = model
        self._data_table_info = data_table_info

    def get_event(self) -> Event:
        return self._event

    def get_form_type(self) -> Type[RegistrationForm]:
        return self._form

    def get_model_type(self) -> Type[RegistrationModel]:
        return self._model

    def get_data_table_info(self) -> DataTableInfo:
        return self._data_table_info


class FormController(ABC):

    def __init__(self, module_info: ModuleInfo):
        self._module_info = module_info
        self._context = module_info.get_form_context()

    def get_request_handler(self, request) -> Any:
        """
        Render the requested form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        """
        event_quotas = copy.deepcopy(self._context.get_event().get_quotas())
        entries = self._fetch_registration_info(event_quotas)
        registrations = EventRegistrations(event_quotas, entries)
        form = self._context.get_form_type()()
        return self._render_index_view(registrations, form, datetime.now())

    def post_request_handler(self, request) -> Any:
        """
        Handle the submitted form for this event.
        Can be overridden in inheriting class to alter the behaviour.
        Although overriding of this method should be avoided and other
        methods that are used during the post routine should be
        preferred for overriding.
        """
        event_quotas = self._get_quota_copy()
        return self._post_routine(event_quotas, self._context.get_form_type()())

    def get_data_request_handler(self, request) -> Any:
        event_quotas = self._get_quota_copy()
        return self._render_data_view(event_quotas)

    def get_data_csv_request_handler(self, request) -> Any:
        event_quotas = self._get_quota_copy()
        entries = self._fetch_registration_info(event_quotas)
        form_name = self._module_info.get_form_name()
        return _export_to_csv(form_name, self._context.get_data_table_info(), entries)

    def _get_quota_copy(self) -> Dict[str, Quota]:
        return copy.deepcopy(self._context.get_event().get_quotas())

    def _matching_identity(self, firstname0, firstname1, lastname0, lastname1, email0, email1) -> bool:
        return (firstname0 != '' and lastname0 != '' and email0 != '' and
                firstname0 == firstname1 and lastname0 == lastname1 and email0 == email1)

    def _find_from_entries(self, entries: Iterable[RegistrationModel], form: RegistrationForm) -> Tuple[bool, str]:
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
                registered_participants = list(m.get_required_participants()) + list(m.get_optional_participants())
                for p in registered_participants:
                    if self._matching_identity(p.get_firstname(), firstname,
                                               p.get_lastname(), lastname,
                                               p.get_email(), email):
                        return True, '{} {} on jo ilmoittautunut.'.format(firstname, lastname)

        return False, ''

    def _find_in_self(self, form: RegistrationForm) -> Tuple[bool, str]:
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

    def _get_email_recipients(self, model: RegistrationModel) -> Collection[BaseParticipant]:
        """
        A method to get all email recipients to whom an email
        concerning current registration should be sent to.
        Can be overridden in inheriting classes to alter behaviour.
        """
        participants = list(model.get_required_participants()) + list(model.get_optional_participants())
        recipients = []
        emails = set()
        for p in participants:
            email = p.get_email()
            if len(email) != 0 and email not in emails:
                recipients.append(p)
                emails.add(email)

        return recipients

    def _participant_to_email_recipient(self, participant: BaseParticipant) -> EmailRecipient:
        return EmailRecipient(participant.get_firstname(), participant.get_lastname(), participant.get_email())

    @abstractmethod
    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        pass

    def _post_routine(self, event_quotas: Dict[str, Quota], form: RegistrationForm) -> Any:
        # MEMO: This routine is prone to data race since it does not use transactions
        nowtime: datetime = datetime.now()
        entries = self._fetch_registration_info(event_quotas)
        registrations = EventRegistrations(event_quotas, entries)

        error_msg = self._check_form_submit(registrations, form, event_quotas, nowtime)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(registrations, form, nowtime)

        model = self._form_to_model(form, nowtime)
        error_msg = self._insert_model(model)
        if len(error_msg) != 0:
            flash(error_msg)
            return self._render_index_view(registrations, form, nowtime)

        model.set_is_in_reserve(self._calculate_reserve_status(model, event_quotas))

        self._send_emails(model)
        flash(_make_success_msg(model.get_is_in_reserve()))
        registrations.add_new_registration(model)
        return self._post_routine_output(registrations, form, nowtime)

    def _post_routine_output(self, registrations, form: RegistrationForm, nowtime) -> Any:
        """
        A method that handles post request output rendering.
        Can be overridden in inheriting classes to alter behaviour.
        """
        return self._render_index_view(registrations, form, nowtime)

    def _check_form_submit(self, registrations: EventRegistrations,
                           form: RegistrationForm, event_quotas: Dict[str, Quota], nowtime: datetime) -> str:
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

        if nowtime < event.get_registration_start_time():
            return 'Ilmoittautuminen ei ole alkanut'

        if nowtime > event.get_registration_end_time():
            return 'Ilmoittautuminen on päättynyt'

        form_quota_counts = form.get_quota_counts()
        msg = self._check_quota_registration_times(nowtime, event_quotas, form_quota_counts)
        if len(msg) != 0:
            return msg

        msg = self._check_quota_counts(event_quotas, form_quota_counts)
        if len(msg) != 0:
            return msg

        (found, msg) = self._find_from_entries(registrations.get_entries(), form)
        if found:
            return msg or 'Olet jo ilmoittautunut'

        (found, msg) = self._find_in_self(form)
        if found:
            return msg

        return ""

    def _form_to_model(self, form: RegistrationForm, nowtime: datetime) -> RegistrationModel:
        """
        A method to convert form into a model.
        Can be overridden in inheriting classes to alter behaviour.
        """
        model_factory = self._module_info.get_type_info().get_model_factory_method()
        required_count = len(form.get_required_participants())
        optional_count = len(form.get_optional_participants())
        model = model_factory(required_count, optional_count, nowtime)
        form.populate_obj(model)

        # MEMO: Clear out empty entries to prevent invalid enum values from causing an error.
        participants = model.get_required_participants()
        for p in participants[:]:
            if not p.is_filled():
                participants.remove(p)

        participants = model.get_optional_participants()
        for p in participants[:]:
            if not p.is_filled():
                participants.remove(p)

        return model

    def _validate_form(self, form: RegistrationForm) -> bool:
        valid = form.get_required_participants().validate(form)
        other_attributes = form.get_other_attributes()
        valid = other_attributes.validate(other_attributes.form) and valid
        for participant in form.get_optional_participants():
            for field in participant:
                if field.data:
                    valid = participant.validate(participant.form) and valid
                    break

        return valid

    def _check_quota_registration_times(self, nowtime: datetime,
                                        event_quotas: Dict[str, Quota], form_quotas: Iterable[Quota]) -> str:
        time_violation_messages = []
        for form_quota in form_quotas:
            name = form_quota.get_name()
            if name not in event_quotas.keys():
                return "Kelvoton arvo."

            quota = event_quotas[name]
            start = quota.get_quota_registration_start()
            end = quota.get_quota_registration_end()
            if start is not None and start > nowtime:
                time_violation_messages.append("Ilmoittautuminen ei ole alkanut kiintiölle " + quota.get_name())
            if end is not None and end < nowtime:
                time_violation_messages.append("Ilmoittautuminen on päättynyt kiintiölle " + quota.get_name())

        if len(time_violation_messages) > 0:
            return '\n'.join(time_violation_messages)

        return ""


    def _check_quota_counts(self, event_quotas: Dict[str, Quota],
                            form_quotas: Iterable[Quota]) -> str:
        """
        Ensure that no quota has been exceeded.
        """
        for form_quota in form_quotas:
            name = form_quota.get_name()
            if name not in event_quotas.keys():
                return "Kelvoton arvo."

            event_quota = event_quotas[name]
            registration_count = event_quota.get_registrations() + form_quota.get_quota()
            if registration_count > event_quotas[name].get_max_quota():
                if name != Quota.default_quota_name():
                    return 'Ilmoittautuminen on jo täynnä kiintiön {} osalta.'.format(name)
                return 'Ilmoittautuminen on jo täynnä.'

        return ""

    def _fetch_registration_info(self, event_quotas: Dict[str, Quota]) -> Collection[RegistrationModel]:
        entries: Collection[RegistrationModel] = self._context.get_model_type().query.all()
        self._count_registration_quotas(event_quotas, entries)
        self._calculate_reserve_statuses(entries, event_quotas)
        return entries

    def _count_registration_quotas(self, event_quotas: Dict[str, Quota], entries: Collection[RegistrationModel]) -> None:
        """
        A method to count the number of event participants per quota.
        MEMO: Modifies event_quotas
        """
        for entry in entries:
            for quota in entry.get_quota_counts():
                event_quota = event_quotas[quota.get_name()]
                event_quota.set_registrations(event_quota.get_registrations() + quota.get_quota())

    def _calculate_reserve_statuses(self, entries: Iterable[RegistrationModel],
                                    event_quotas: Dict[str, Quota]) -> None:

        
        # keep track of how many non-reserve spots are left
        # quota_name : quota count
        quota_limits: Dict[str, int] = {}
        for quota_name in event_quotas:
            quota_limits[quota_name] = event_quotas[quota_name].get_quota()
            
        for entry in entries:
            entry.set_is_in_reserve(self._calculate_reserve_status_for_entry(entry, event_quotas, quota_limits))

    def _calculate_reserve_status_for_entry(self, \
                                            entry : RegistrationModel, \
                                            event_quotas: Dict[str, Quota], \
                                            quota_limits: Dict[str, int]):
        """
        called from _calculate_reserve_statuses
        """
        
        reserve = False

        # @NOTE 2023:
        # quota_count : Quota
        # Entries can occupy multible quotas if there are options for avec etc.
        #
        # Still, it seems that quota_count is a Quota object with only name filled in
        # quota := 1, and reserve := 0.
        # Not really sure why entries don't just hold a name to the quota they occupy

        for quota_count in entry.get_quota_counts():
            quota_name = quota_count.get_name()

            quota_limits[quota_name] -= 1;

            if quota_limits[quota_name] < 0:
                reserve = True
            
            #reserve = reserve or event_quotas[quota_name].get_registrations() >= event_quotas[quota_name].get_quota()

        return reserve

        
    def _calculate_reserve_status(self, entry: RegistrationModel,
                                  event_quotas: Dict[str, Quota]) -> bool:
        # MEMO: If any registration participant is on reserve space, the whole registration
        #       is considered to be on reserve.

        
        # @NOTE 2023:
        # quota_count : Quota
        # Entries can occupy multible quotas if there are options for avec etc.
        # 
        # Still, it seems that quota_count is a Quota object with only name filled in
        # quota := 1, and reserve := 0.
        # Not really sure why entries don't just hold a name to the quota they occupy

        reserve = False

        for quota_count in entry.get_quota_counts():
            quota_name = quota_count.get_name()
            
            reserve = reserve or event_quotas[quota_name].get_registrations() >= event_quotas[quota_name].get_quota()

        return reserve

    def _insert_model(self, model: RegistrationModel) -> str:
        try:
            db.session.add(model)
            db.session.commit()
            return ''

        except Exception as e:
            db.session.rollback()
            print(e)

        return 'Tietokanta virhe. Yritä uudestaan.'

    def _send_emails(self, model: RegistrationModel) -> None:
        subject = self._context.get_event().get_title()
        for recipient in self._get_email_recipients(model):
            msg = self._get_email_msg(recipient, model, model.get_is_in_reserve())
            send_email(msg, subject, self._participant_to_email_recipient(recipient))

    def _render_index_view(self, registrations: EventRegistrations,
                           form: RegistrationForm, nowtime, **extra_template_args) -> Any:
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

    def _render_data_view(self, event_quotas: Dict[str, Quota]) -> Any:
        """
        A helper method to render a data view template.
        """
        entries = self._fetch_registration_info(event_quotas)
        registrations = EventRegistrations(event_quotas, entries)
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

    def __init__(self, required_participant_map: Iterable[Tuple[str, str]],
                 optional_participant_map: Iterable[Tuple[str, str]],
                 other_attributes_map: Iterable[Tuple[str, str]],
                 max_required_participants: int,
                 max_optional_participants: int):

        self._required_participant = self._unpack(required_participant_map)
        self._optional_participant = self._unpack(optional_participant_map)
        self._other_attributes = self._unpack(other_attributes_map)
        self._max_required_participants = max_required_participants
        self._max_optional_participants = max_optional_participants

    def _unpack(self, attribute_map: Iterable[Tuple[str, str]]) -> Tuple[Collection[str], Collection[str]]:
        names = []
        headers = []
        for name, header in attribute_map:
            names.append(name)
            headers.append(header)

        return names, headers

    def get_required_participant_attributes_getters(self) -> Collection[str]:
        return self._required_participant[0]

    def get_optional_participant_attributes_getters(self) -> Collection[str]:
        return self._optional_participant[0]

    def get_other_attributes_getters(self) -> Collection[str]:
        return self._other_attributes[0]

    def _get_required_participant_headers(self) -> Collection[str]:
        return self._required_participant[1]

    def _get_optional_participant_headers(self) -> Collection[str]:
        return self._optional_participant[1]

    def _get_other_attribute_headers(self) -> Collection[str]:
        return self._other_attributes[1]

    def get_max_required_participants(self) -> int:
        return self._max_required_participants

    def get_max_optional_participants(self) -> int:
        return self._max_optional_participants

    def make_header_row(self):

        def make_headers(names: Iterable[str], start: int, end: int, omit_numbering: bool):
            for i in range(start, start + end):
                for name in names:
                    yield f'{name}' if omit_numbering else f'{name}_{i + 1}'

        omit_numbering = self._max_required_participants + self._max_optional_participants == 1

        yield from make_headers(self._get_required_participant_headers(),
                                0, self._max_required_participants, omit_numbering)
        yield from make_headers(self._get_optional_participant_headers(),
                                self._max_required_participants, self._max_optional_participants, omit_numbering)
        yield from [name for name in self._get_other_attribute_headers()]

    def model_to_row(self, entry: RegistrationModel):

        def participants_to_row(participants: Collection[BaseParticipant],
                                attributes: Collection[str],
                                max_count: int) -> Iterable[str]:
            for participant in participants:
                yield from [
                    str(getattr(participant, attribute)())
                    for attribute in attributes
                ]

            yield from [''] * max(max_count - len(participants), 0) * len(attributes)

        yield from participants_to_row(entry.get_required_participants(),
                                       self.get_required_participant_attributes_getters(),
                                       self._max_required_participants)
        yield from participants_to_row(entry.get_optional_participants(),
                                       self.get_optional_participant_attributes_getters(),
                                       self._max_optional_participants)
        yield from [str(getattr(entry.get_other_attributes(), attribute)())
                    for attribute in self.get_other_attributes_getters()]


def _export_to_csv(form_name: str,
                   table_info: DataTableInfo,
                   entries: Collection[RegistrationModel]) -> Any:
    """
    A method to export and send out the event's registration data as a CSV file
    """
    os.system('mkdir csv')
    csv_path = export_to_csv(form_name, table_info, entries)
    (folder, file) = os.path.split(csv_path)
    try:
        return send_from_directory(directory=folder, filename=file, as_attachment=True)
    except FileNotFoundError as e:
        print(e)
        abort(404)
