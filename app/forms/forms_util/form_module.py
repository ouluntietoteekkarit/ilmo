from pathlib import Path
from typing import Type, Union
from os.path import split, splitext

from app.forms.forms_util.form_controller import FormController


class FormModule:
    """
    A class to provide a programming interface for form python modules.
    """

    def __init__(self, controller_type: Type[FormController], is_active: bool, form_name: str):
        self._controller_type = controller_type
        self._is_active = is_active
        self._form_name = form_name

    def get_controller_type(self) -> Type[FormController]:
        return self._controller_type

    def is_active(self) -> bool:
        return self._is_active

    def get_form_name(self) -> str:
        return self._form_name


def file_path_to_form_name(path: Union[str, Path]):
    return splitext(split(path)[1])[0]
