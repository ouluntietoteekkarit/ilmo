from __future__ import annotations

from datetime import datetime
from typing import List

from wtforms.validators import InputRequired, Length

from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_binding_registration_consent, \
    make_attribute_telegram, make_attribute_allergies, make_attribute_phone_number
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import BaseParticipant
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info


# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "404: Land Not Found -risteilyn yhteiskuljetus"
_is_enabled = True
_start_date = datetime(2025, 11, 24, 12, 00, 00)
_end_date = datetime(2026, 1, 5, 23, 59, 59)


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()
        phone = recipient.get_phone_number()
        telegram = recipient.get_telegram()
        allergies = recipient.get_allergies()

        if reserve:
            result = ' '.join([
                f"Tervehdys, {firstname}!\n",
                "Olet ilmoittautunut 404: Land Not Found -risteilyn yhteiskuljetusexculle. Olet varasijalla.",
                "Jos bussiin vapautuu paikkoja, sinuun voidaan olla yhteydessä sähköpostitse.",
                "\n\nTässä vielä syöttämäsi tiedot: ",
                f"\nNimi: {firstname} {lastname}",
                f"\nSähköposti: {email}",
                f"\nPuhelinnumero: {phone}",
                f"\nTelegram: {telegram}",
                f"\nAllergiat: {allergies}",
                "\nKysymyksistä voit olla yhteydessä sähköpostitse jukeboxi@otit.fi tai Telegramissa @jukeboxxxi."
                "\n\nTähän sähköpostiin ei voi vastata.",
                "\n-----",
                "\nGreetings, ", firstname, "!\n",
                "You have signed up for the 404: Land Not Found cruise shared transportation. You are on the waiting list.",
                "If spots become available, you may be contacted via email.",
                "\n\nHere are the details you provided: ",
                f"\nName: {firstname} {lastname}",
                f"\nEmail: {email}",
                f"\nPhone: {phone}",
                f"\nTelegram: {telegram}",
                f"\nAllergies: {allergies}",
                "\nFor questions, you can contact us via email at jukeboxi@otit.fi or on Telegram @jukeboxxxi.",
                "\n\nYou cannot reply to this email."
            ])
        else:
            result = ' '.join([
                f"Tervehdys, {firstname}!\n",
                "\nOlet ilmoittautunut 404: Land Not Found -risteilyn yhteiskuljetusexculle. Tässä vielä syöttämäsi tiedot: ",
                f"\nNimi: {firstname} {lastname}",
                f"\nSähköposti: {email}",
                f"\nPuhelinnumero: {phone}",
                f"\nTelegram: {telegram}",
                f"\nAllergiat: {allergies}",
                "\n\nBussin alustava lähtöaika on perjantaiaamuna 9.1.2026. Tarkemmat tiedot matkasta sekä maksuohjeet lähetetään myöhemmin sähköpostitse.",
                "\n\nJos sairastut tai olet muutoin estynyt osallistumasta, ilmoitathan asiasta pikimmiten,",
                "jotta paikkasi voidaan vapauttaa varasijalla olevalle."
                "\nKysymyksistä tai poissaoloilmoituksista voit olla yhteydessä sähköpostitse jukeboxi@otit.fi tai Telegramissa @jukeboxxxi."
                "\n\nTähän sähköpostiin ei voi vastata.",
                "\n-----",
                f"\nGreetings, {firstname}!\n"
                "\nYou have signed up for the 404: Land Not Found cruise shared transportation. Here are the details you provided: ",
                f"\nName: {firstname} {lastname}",
                f"\nEmail: {email}",
                f"\nPhone: {phone}",
                f"\nTelegram: {telegram}",
                f"\nAllergies: {allergies}",
                "\n\nThe bus is preliminarily scheduled to depart on the morning of Friday, January 9th, 2026. More detailed information about the trip and payment instructions will be sent later via email.",
                "\n\nIf you fall ill or are otherwise unable to attend, please inform us as soon as possible,",
                "so your spot can be given to someone on the waiting list.",
                "\nFor questions or absence notifications, you can contact us via email at jukeboxi@otit.fi or on Telegram @jukeboxxxi.",
                "\n\nYou cannot reply to this email."
            ])

        return result


def hide_title():
    return True

def _get_quotas() -> List[Quota]:
    return [
        Quota('Matkanjohtaja', 1, 0),
        Quota('Osallistuja', 54, 100),]

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_telegram(validators=[]),
    make_attribute_allergies(),
    make_attribute_quota(_QuotaEnum, validators=[InputRequired()])
]


other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent(validators=[InputRequired()]),
    make_attribute_binding_registration_consent(validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event(_event_name,
               _start_date,
               _end_date,
               _get_quotas(),
               _types.asks_name_consent(),
               True)

_module_info = ModuleInfo(_Controller, _is_enabled, _form_name, _event, _types)
