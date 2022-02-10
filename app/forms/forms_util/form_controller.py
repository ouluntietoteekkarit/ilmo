from abc import ABC, abstractmethod


class FormController(ABC):

    @abstractmethod
    def request_handler(self, request):
        pass
