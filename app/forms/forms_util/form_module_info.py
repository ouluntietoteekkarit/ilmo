from __future__ import annotations
from pathlib import Path
from typing import Type, Union, TYPE_CHECKING
from os.path import split, splitext

if TYPE_CHECKING:
    from .form_controller import FormController


class ModuleInfo:
    """
    A class to provide a programming interface for form python modules.
    """

    def __init__(self, controller_type: Type[FormController], is_active: bool, form_name: str):
        self._controller_type = controller_type
        self._is_active = is_active
        self._form_name = form_name
        self._form_endpoint_get_index = ""
        self._form_endpoint_post_index = ""
        self._form_endpoint_get_data = ""
        self._form_endpoint_get_data_csv = ""

    def get_controller_type(self) -> Type[FormController]:
        return self._controller_type

    def is_active(self) -> bool:
        return self._is_active

    def get_form_name(self) -> str:
        return self._form_name

    def get_endpoint_get_index(self) -> str:
        return self._form_endpoint_get_index

    def set_endpoint_get_index(self, path: str) -> None:
        self._form_endpoint_get_index = path

    def get_endpoint_post_index(self) -> str:
        return self._form_endpoint_post_index

    def set_endpoint_post_index(self, endpoint: str) -> None:
        self._form_endpoint_post_index = endpoint

    def get_endpoint_get_data(self) -> str:
        return self._form_endpoint_get_data

    def set_endpoint_get_data(self, endpoint: str) -> None:
        self._form_endpoint_get_data = endpoint

    def get_endpoint_get_data_csv(self) -> str:
        return self._form_endpoint_get_data_csv

    def set_endpoint_get_data_csv(self, endpoint: str) -> None:
        self._form_endpoint_get_data_csv = endpoint


def file_path_to_form_name(path: Union[str, Path]) -> str:
    # MEMO: Add sanitation if needed
    return splitext(split(path)[1])[0]
