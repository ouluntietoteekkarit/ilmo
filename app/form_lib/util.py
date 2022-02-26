from __future__ import annotations
from typing import Collection

from app.form_lib.forms import FormTypeFactory
from app.form_lib.lib import BaseAttribute, TypeContainer
from app.form_lib.models import DbTypeFactory


def make_types(required_participant_attributes: Collection[BaseAttribute],
               optional_participant_attributes: Collection[BaseAttribute],
               other_attributes: Collection[BaseAttribute],
               required_participant_count: int,
               optional_participant_count: int,
               form_name: str) -> TypeContainer:

    factories = {
        'form_type': FormTypeFactory(required_participant_attributes, optional_participant_attributes,
                                     other_attributes, required_participant_count,
                                     optional_participant_count),
        'model_type': DbTypeFactory(required_participant_attributes, optional_participant_attributes,
                                    other_attributes, required_participant_count,
                                    optional_participant_count, form_name)
    }
    types = {}
    for name, factory in factories.items():
        types[name] = factory.make_type()

    return TypeContainer(**types)
