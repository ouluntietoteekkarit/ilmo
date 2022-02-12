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
