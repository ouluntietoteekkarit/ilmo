from __future__ import annotations
from pathlib import Path
from typing import Type, Union, TYPE_CHECKING, Tuple
from os.path import split, splitext

from .util import TypeInfo
from .form_controller import FormContext

if TYPE_CHECKING:
    from .form_controller import FormController, DataTableInfo
    from .event import Event


class ModuleInfo:
    """
    A class to provide a programming interface for form python modules.
    The cosntructor has some functionality that allows eliminating
    boilerplate code from form scripts.
    """

    def __init__(self, controller_type: Type[FormController], is_active: bool,
                 form_name: str, event: Event, type_info: TypeInfo):
        self._controller_type = controller_type
        self._is_active = is_active
        self._form_name = form_name
        self._type_info = type_info
        self._context = FormContext(event,
                                    type_info.get_form_type(),
                                    type_info.get_model_type(),
                                    type_info.get_data_info())
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

    def get_type_info(self) -> TypeInfo:
        return self._type_info

    def get_form_context(self) -> FormContext:
        return self._context

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


def make_form_name(path: Union[str, Path]) -> str:
    """Reduces a file path plain filename"""
    # MEMO: Add sanitation if needed
    return splitext(split(path)[1])[0]
