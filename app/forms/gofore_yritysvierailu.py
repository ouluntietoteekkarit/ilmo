from __future__ import annotations

from datetime import datetime
from typing import List

from wtforms.validators import InputRequired, Email, Length

from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_other_attributes, make_attribute_binding_registration_consent, \
    make_attribute_telegram, make_attribute_allergies
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.guilds import Guild, GUILD_OTIT, GUILD_BLANKO, GUILD_SIK, GUILD_OLTO
from app.form_lib.lib import BaseParticipant, EnumAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices, get_guild_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info


# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Goforen yritysvierailu"
_is_enabled = True
_start_date = datetime(2025, 11, 17, 18, 00, 00)
_end_date = datetime(2025, 11, 21, 11, 59, 59)


class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        firstname = recipient.get_firstname()
        lastname = recipient.get_lastname()
        email = recipient.get_email()
        telegram = recipient.get_telegram()
        allergies = recipient.get_allergies()

        if reserve:
            result = ' '.join([
                f"Tervehdys, {firstname}!\n",
                "Olet ilmoittautunut Goforen toimistoexcursiolle 27.11.2025. Olet varasijalla.",
                "Jos yritysvierailulle vapautuu paikkoja, sinuun voidaan olla yhteydessä sähköpostitse.",
                "\n\nTässä vielä syöttämäsi tiedot: ",
                "\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email,
                "\nTelegram: ", telegram,
                "\nAllergiat: ", allergies,
                "\n\nTähän sähköpostiin ei voi vastata.",
                "\n-----",
                "\nGreetings, ", firstname, "!\n",
                "You have signed up for the Gofore office excursion on November 27th, 2025. You are on the waiting list.",
                "If spots become available, you may be contacted via email.",
                "\n\nHere are the details you provided: ",
                "\nName: ", firstname, lastname,
                "\nEmail: ", email,
                "\nTelegram: ", telegram,
                "\nAllergies: ", allergies,
                "\n\nYou cannot reply to this email."
            ])
        else:
            result = ' '.join([
                f"Tervehdys, {firstname}!\n",
                "\nOlet ilmoittautunut Goforen toimistoexcursiolle torstaina 27.11.2025. Tässä vielä syöttämäsi tiedot: ",
                "\nNimi: ", firstname, lastname,
                "\nSähköposti: ", email,
                "\nTelegram: ", telegram,
                "\nAllergiat: ", allergies,
                "\n\nVierailu alkaa torstaina heti klo 17.00, joten saavuthan ajoissa paikalle. Toimisto sijaitsee vanhalla paloasemalla, osoitteessa Kauppurienkatu 24.",
                "\nSisäänkäynti on Kauppurienkadun puolella."
                "Jos sairastut tai olet muutoin estynyt osallistumasta vierailulle, ilmoitathan asiasta pikimmiten,",
                "jotta paikkasi voidaan vapauttaa varasijalla olevalle."
                "\nKysymyksistä tai poissaoloilmoituksista voit olla yhteydessä sähköpostitse ulkoministeri@otit.fi tai Telegramissa @AKoponen."
                "\n\nTähän sähköpostiin ei voi vastata.",
                "\n-----",
                "\nGreetings, ", firstname, "!\n"
                "\nYou have signed up for the OP Financial Group office excursion on Thursday, November 27th, 2025. Here are the details you provided: ",
                "\nName: ", firstname, lastname,
                "\nEmail: ", email,
                "\nTelegram: ", telegram,
                "\nAllergies: ", allergies,
                "\n\nThe visit starts promptly at 17:00 on Thursday, so please arrive on time. The office is located at the old fire station, at Kauppurienkatu 24.",
                "\nThe entrance is on the Kauppurienkatu side."
                "If you fall ill or are otherwise unable to attend, please inform us as soon as possible,",
                "so your spot can be given to someone on the waiting list.",
                "\nFor questions or absence notifications, you can contact us via email at ulkoministeri@otit.fi or on Telegram @AKoponen.",
                "\n\nYou cannot reply to this email."
            ])

        return result

def _get_quotas() -> List[Quota]:
    return [
        Quota('Osallistuja', 25, 100),
    ]


def hide_title():
    return True

_QuotaEnum = choices_to_enum(_form_name,
                             'quota',
                             get_quota_choices(_get_quotas()))

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired()]),
    make_attribute_telegram(validators=[InputRequired()]),
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
