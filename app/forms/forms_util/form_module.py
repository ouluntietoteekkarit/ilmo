from typing import Type

from app.forms.forms_util.form_controller import FormController


class FormModule:
    """
    A class to provide a programming interface for form python modules.
    """

    def __init__(self, controller_type: Type[FormController], is_active: bool, form_name: str):
        self.controller_type = controller_type
        self.is_active = is_active
        self.form_name = form_name

    def get_controller_type(self):
        return self.controller_type

    def is_active(self):
        return self.is_active()

    def get_form_name(self):
        return self.form_name
