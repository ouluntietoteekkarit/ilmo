from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Type

from wtforms.validators import Email

from app.form_lib.lib import BaseAttribute, StringAttribute, ATTRIBUTE_NAME_FIRSTNAME, ATTRIBUTE_NAME_LASTNAME, \
    ATTRIBUTE_NAME_EMAIL, ATTRIBUTE_NAME_PHONE_NUMBER, EnumAttribute, ATTRIBUTE_NAME_DEPARTURE_LOCATION, \
    ATTRIBUTE_NAME_QUOTA, BoolAttribute, ATTRIBUTE_NAME_NAME_CONSENT, ATTRIBUTE_NAME_BINDING_REGISTRATION_CONSENT, \
    ATTRIBUTE_NAME_PRIVACY_CONSENT, BaseParticipant, ListAttribute, ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, \
    ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, BaseOtherAttributes, ObjectAttribute, ATTRIBUTE_NAME_OTHER_ATTRIBUTES, \
    ATTRIBUTE_NAME_ALLERGIES


def make_attribute_firstname(**extra_args: Dict[str, Any]) -> BaseAttribute:
    return StringAttribute(ATTRIBUTE_NAME_FIRSTNAME, 'Etunimi', 'Etunimi', 50, **extra_args)


def make_attribute_lastname(**extra_args: Dict[str, Any]) -> BaseAttribute:
    return StringAttribute(ATTRIBUTE_NAME_LASTNAME, 'Sukunimi', 'Sukunimi', 50, **extra_args)


def make_attribute_email(**extra_args: Dict[str, Any]) -> BaseAttribute:
    extra_args.setdefault('validators', [])
    extra_args['validators'] += [Email()]

    return StringAttribute(ATTRIBUTE_NAME_EMAIL, 'Sähköposti', 'Sähköposti', 100, **extra_args)


def make_attribute_phone_number(**extra_args: Dict[str, Any]) -> BaseAttribute:
    return StringAttribute(ATTRIBUTE_NAME_PHONE_NUMBER, 'Puhelinnumero', 'Puhelinnumero', 20, **extra_args)


def make_attribute_departure_location(enum_type: Type[Enum], **extra_args: Dict[str, Any]) -> BaseAttribute:
    return EnumAttribute(ATTRIBUTE_NAME_DEPARTURE_LOCATION, 'Lähtöpaikka', 'Lähtöpaikka', enum_type, **extra_args)


def make_attribute_quota(enum_type: Type[Enum], label: str = 'Kiintiö', short_label: str = 'Kiintiö', **extra_args: Dict[str, Any]) -> BaseAttribute:
    return EnumAttribute(ATTRIBUTE_NAME_QUOTA, label, short_label, enum_type, **extra_args)


def make_attribute_allergies(**extra_args: Dict[str, Any]) -> BaseAttribute:
    return StringAttribute(ATTRIBUTE_NAME_ALLERGIES, 'Erityisruokavaliot/allergiat', 'Erityisruokavaliot', 200, **extra_args)


def make_attribute_name_consent(txt: str = "", **extra_args: Dict[str, Any]) -> BaseAttribute:
    if len(txt) == 0:
        txt = 'Sallin nimeni julkaisemisen osallistujalistassa tällä sivulla'
    # MEMO: Come up with a solution to this.
    # form.asks_name_consent = True
    return BoolAttribute(ATTRIBUTE_NAME_NAME_CONSENT, txt, 'Sallin nimenjulkaisun', **extra_args)


def make_attribute_binding_registration_consent(txt: str = "", **extra_args: Dict[str, Any]) -> BaseAttribute:
    if len(txt) == 0:
        txt = 'Ymmärrän, että ilmoittautuminen on sitova'
    return BoolAttribute(ATTRIBUTE_NAME_BINDING_REGISTRATION_CONSENT, txt, 'Sitoudun ilmoittautumiseen', **extra_args)


def make_attribute_privacy_consent(txt: str = "", **extra_args: Dict[str, Any]) -> BaseAttribute:
    if len(txt) == 0:
        txt = 'Olen lukenut tietosuojaselosteen ja hyväksyn tietojen käytön tapahtuman järjestämisessä'
    return BoolAttribute(ATTRIBUTE_NAME_PRIVACY_CONSENT, txt, 'Hyväksyn tietosuojaselosteen', **extra_args)


def make_attribute_required_participants(participant_type: Type[BaseParticipant], count: int = 1, **extra_args: Dict[str, Any]) -> BaseAttribute:
    return ListAttribute(ATTRIBUTE_NAME_REQUIRED_PARTICIPANTS, '', '', participant_type, count, **extra_args)


def make_attribute_optional_participants(participant_type: Type[BaseParticipant], count: int = 0, **extra_args: Dict[str, Any]) -> BaseAttribute:
    return ListAttribute(ATTRIBUTE_NAME_OPTIONAL_PARTICIPANTS, '', '', participant_type, count, **extra_args)


def make_attribute_other_attributes(form_type: Type[BaseOtherAttributes], **extra_args: Dict[str, Any]) -> BaseAttribute:
    return ObjectAttribute(ATTRIBUTE_NAME_OTHER_ATTRIBUTES, '', '', form_type, **extra_args)
