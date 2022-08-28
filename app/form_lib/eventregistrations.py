from __future__ import annotations

from typing import Dict, List, Collection

from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota


class EventRegistrations:
    """
    A class to hold dynamic registration data
    """

    def __init__(self, event_quotas: Dict[str, Quota], entries: List[RegistrationModel]):
        self._entries = entries
        self._event_quotas = event_quotas

    def get_entries(self) -> Collection:
        return self._entries

    def get_event_quotas(self) -> Dict[str, Quota]:
        return self._event_quotas

    def add_new_registration(self, entry: RegistrationModel) -> None:
        for quota in entry.get_quota_counts():
            event_quota = self._event_quotas[quota.get_name()]
            event_quota.set_registrations(event_quota.get_registrations() + quota.get_quota())

        self._entries.append(entry)
