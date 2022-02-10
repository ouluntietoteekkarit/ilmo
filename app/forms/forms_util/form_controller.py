from abc import ABC, abstractmethod
from typing import Any
import os
from app.sqlite_to_csv import export_to_csv
from flask import send_from_directory, abort, render_template
from .event import Event


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

    def _data_view(self, model, template, **additional_template_args) -> Any:
        """
        A helper method to render a data view template.
        """
        event = self._get_event()
        limit = event.get_participant_limit()
        entries = model.query.all()
        count = len(entries)
        return render_template(template, **{
            'title': '{} data'.format(event.get_name()),
            'entries': entries,
            'count': count,
            'limit': limit,
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
