from __future__ import annotations

from datetime import datetime
from typing import Union


class Quota:
    def __init__(self, name: str, quota: int, reserve_quota: int = 0,
                 registration_start: Union[datetime, None] = None,
                 registration_end: Union[datetime, None] = None):
        self._name = name
        self._quota = quota
        self._reserve_quota = reserve_quota
        self._registration_start = registration_start
        self._registration_end = registration_end

    def get_name(self) -> str:
        return self._name

    def get_quota(self) -> int:
        return self._quota

    def get_reserve_quota(self) -> int:
        return self._reserve_quota

    def get_max_quota(self) -> int:
        return self._quota + self._reserve_quota

    def get_quota_registration_start(self) -> Union[datetime, None]:
        return self._registration_start

    def get_quota_registration_end(self) -> Union[datetime, None]:
        return self._registration_end

    @staticmethod
    def default_quota_name() -> str:
        return '_'

    @staticmethod
    def default_quota(quota: int, reserve_quota: int) -> Quota:
        return Quota(Quota.default_quota_name(), quota, reserve_quota)