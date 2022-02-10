class Event(object):

    def __init__(self, name, start_time, end_time, participant_limit):
        self._name = name
        self._start_time = start_time
        self._end_time = end_time
        self._participant_limit = participant_limit

    def get_name(self):
        return self._name

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time

    def get_participant_limit(self):
        return self._participant_limit

