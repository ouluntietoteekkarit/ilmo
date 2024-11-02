from __future__ import annotations

from datetime import datetime
from typing import Iterable, Dict

from app.form_lib.quota import Quota


class Event(object):
    """
    A readonly class containing event's information.
    """

    def __init__(self, title: str, start_time: datetime,
                 end_time: datetime, quotas: Iterable[Quota],
                 list_participant_names: bool, hide_title=False):
        self._title = title
        self._start_time = start_time
        self._end_time = end_time
        self._list_participant_names = list_participant_names
        self._hide_title = hide_title
        self._participant_limit = 0
        self._max_participant_limit = 0
        self._quotas = {}
        for quota in quotas:
            self._quotas[quota.get_name()] = quota
            self._participant_limit += quota.get_quota()
            self._max_participant_limit += quota.get_max_quota()

    def get_title(self) -> str:
        return self._title

    def hide_title(self) -> bool:
        return self._hide_title

    def get_registration_start_time(self) -> datetime:
        return self._start_time

    def get_registration_end_time(self) -> datetime:
        return self._end_time

    def get_quotas(self) -> Dict[str, Quota]:
        return self._quotas

    def get_participant_limit(self) -> int:
        return self._participant_limit

    def get_max_limit(self) -> int:
        return self._max_participant_limit

    def get_list_participant_name(self) -> bool:
        return self._list_participant_names
