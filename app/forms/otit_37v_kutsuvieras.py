from __future__ import annotations

from datetime import datetime
from typing import List, Collection, Dict

from wtforms.validators import InputRequired, Length, Email

from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_quota, make_attribute_name_consent, \
    make_attribute_privacy_consent, make_attribute_allergies, make_attribute_phone_number, \
    make_attribute_binding_registration_consent
from app.form_lib.drinks import make_enum_usual_sitsi_liquor, make_enum_usual_sitsi_wine, make_enum_usual_avec_drink
from app.form_lib.event import Event
from app.form_lib.form_controller import FormController
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.lib import StringAttribute, BaseParticipant, BoolAttribute, EnumAttribute
from app.form_lib.models import RegistrationModel
from app.form_lib.quota import Quota
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

_form_name = make_form_name(__file__)

_event_name = "Oulun Tietoteekkarit ry 37 vuotta"
_is_enabled = False
_start_date = datetime(2025, 8, 24, 13, 37, 00)
_end_date   = datetime(2025, 9, 15, 23, 59, 59)


class _Controller(FormController):

#    def _fetch_registration_info(self, event_quotas: Dict[str, Quota]) -> Collection[RegistrationModel]:
#        """Override to combine participants from both otit_37v_kutsuvieras and otit_37v forms"""
#        # Get participants from this form (otit_37v_kutsuvieras)
#        entries = list(self._context.get_model_type().query.all())
#
#        # Get participants from the regular form
#        try:
#            from app.forms.otit_37v import _types as regular_types
#            regular_entries = list(regular_types.get_model_type().query.all())
#            entries.extend(regular_entries)
#        except (ImportError, AttributeError):
#            # If regular form doesn't exist or isn't accessible, just use current entries
#            pass
#
#        # Sort all entries by registration time to show in proper chronological order
#        entries.sort(key=lambda x: x.create_time if x.create_time else datetime.min)
#
#        self._count_registration_quotas(event_quotas, entries)
#        self._calculate_reserve_statuses(entries, event_quotas)
#        return entries

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:
        fn = recipient.get_firstname()
        ln = recipient.get_lastname()
        email = recipient.get_email()
        phone = recipient.get_phone_number()
        allergies = recipient.get_allergies()
        toast = recipient.get_toast()
        wine = recipient.get_wine()
        avec_drink = recipient.get_avec_drink()
        seat_pref = recipient.get_seat()
        study_year = recipient.get_study_year()
        sillis_bool = recipient.get_sillis()
        organization = recipient.get_organization()
        greeting = recipient.get_greeting()

        if reserve:
            return f"""Tervehdys, {fn} {ln}!

Ilmoittautumisesi Oulun Tietoteekkarit ry:n 37. vuosijuhliin on vastaanotettu. Huomaathan, että olet varasijalla.
Mikäli vuosijuhliin vapautuu lisää paikkoja, olemme sinuun yhteydessä sähköpostitse.

Tässä vielä ilmoittamasi tiedot:
Nimi: {fn} {ln}
Sähköposti: {email}
Puhelinnumero: {phone}

Alkumalja: {toast}
Viini: {wine}
Kahvin avec: {avec_drink}
Allergiat: {allergies}

Jätätkö tervehdyksen: {greeting}
Edustamasi taho: {organization}
Pöytäseuratoive: {seat_pref}
Opintojen aloitusvuosi: {study_year}
Osallistutko sillikselle: {sillis_bool}

Jos huomaat virheitä ilmoittautumisessasi tai sinulla on jotain kysyttävää, olethan meihin pikimmiten yhteydessä sähköpostitse vuosijuhlavastaava@otit.fi tai Telegramissa @AKoponen.
Tähän sähköpostiin ei voi vastata.

-----
Greetings, {fn} {ln}!

Your registration for Oulun Tietoteekkarit ry's 37th annual celebration has been received. Please note that you are on the waiting list.
If more spots become available, we will contact you by email.

Here are the details you provided:
First name: {fn}
Last name: {ln}
Email: {email}
Phone number: {phone}

Toast drink: {toast}
Wine: {wine}
Avec: {avec_drink}
Allergies: {allergies}

Greeting: {greeting}
Organization/entity: {organization}
Seating preference: {seat_pref}
Start year of studies: {study_year}
Sillis brunch (15 €): {sillis_bool}

If you notice any errors in your registration or have any questions, please don't hesitate to email vuosijuhlavastaava@otit.fi or send a message on Telegram @AKoponen.
This is an automated message, please do not reply."""
        else:
            return f"""Tervehdys, {fn}!

Ilmoittautumisesi Oulun Tietoteekkarit ry:n 37. vuosijuhliin on vastaanotettu. Lämpimästi tervetuloa!
Lähetämme ilmoittautumisajan sulkeuduttua lisätietoja maksusta sekä vuosijuhlien käytännöistä sähköpostitse.

Tässä vielä ilmoittamasi tiedot:
Nimi: {fn} {ln}
Sähköposti: {email}
Puhelinnumero: {phone}

Alkumalja: {toast}
Viini: {wine}
Kahvin avec: {avec_drink}
Allergiat: {allergies}

Jätätkö tervehdyksen: {greeting}
Edustamasi taho: {organization}
Pöytäseuratoive: {seat_pref}
Opintojen aloitusvuosi: {study_year}
Osallistutko sillikselle: {sillis_bool}

Jos huomaat virheitä ilmoittautumisessasi tai sinulla on jotain kysyttävää, olethan pikimmiten yhteydessä sähköpostitse vuosijuhlavastaava@otit.fi tai Telegramissa @AKoponen.
Tähän sähköpostiin ei voi vastata.

-----

Greetings, {fn}!

Your registration for Oulun Tietoteekkarit ry's 37th annual celebration has been received. A warm welcome!
After the registration period has ended, we will send more information about the payment and the event arrangements via email.

Here are the details you provided:
First name: {fn}
Last name: {ln}
Email: {email}
Phone number: {phone}

Toast drink: {toast}
Wine: {wine}
Avec: {avec_drink}
Allergies: {allergies}

Greeting: {greeting}
Organization/entity: {organization}
Seating preference: {seat_pref}
Start year of studies: {study_year}
Sillis brunch (15 €): {sillis_bool}

If you notice any errors in your registration or have any questions, please don't hesitate to email vuosijuhlavastaava@otit.fi or send a message on Telegram @AKoponen.
This is an automated message, please do not reply."""

def _get_quotas() -> List[Quota]:
    return [
        Quota("Osallistuja", 150, 100),
    ]

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_get_quotas()))
_ToastEnum = EnumAttribute('toast', 'Alkumalja | Toast', 'Alkumalja', make_enum_usual_sitsi_liquor(_form_name), validators=[InputRequired()])
_WineEnum = EnumAttribute('wine', 'Viini | Wine', 'Viini', make_enum_usual_sitsi_liquor(_form_name), validators=[InputRequired()])
_AvecDrinkEnum = EnumAttribute('avec_drink', 'Avec', 'Avec-juoma', make_enum_usual_avec_drink(_form_name), validators=[InputRequired()])
_AvecBool = BoolAttribute("avec", "Minulla on avec | I'm bringing a plus one", 'Avec mukana')

_SeatPref = StringAttribute("seat", 'Pöytäseuratoive | Seating preference', 'Avecin nimi', 60)
_StudyStartYear = StringAttribute("study_year", 'Opintojen aloitusvuosi | Start year of studies', 'Aloitusvuosi', 10)
_SillisBool = BoolAttribute("sillis", "Osallistun sillikselle (15 €) | I am attending the sillis brunch (€15)", 'Sillis')

_Greeting = BoolAttribute("greeting", "Haluan jättää tervehdyksen | I would like to leave a greeting", 'Tervehdys')
_Organization = StringAttribute("organization", "Edustamanne taho | Organization/entity you're representing", 'Taho', 60, validators=[InputRequired()])

participant_attributes = [
    make_attribute_firstname(validators=[InputRequired(), Length(max=20)]),
    make_attribute_lastname(validators=[InputRequired(), Length(max=30)]),
    make_attribute_email(validators=[InputRequired(), Email()]),
    make_attribute_phone_number(validators=[InputRequired()]),
    make_attribute_allergies(),
    _ToastEnum,
    _WineEnum,
    _AvecDrinkEnum,
    _SeatPref,
    _StudyStartYear,
    _SillisBool,
    _Greeting,
    _Organization,

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
               _types.asks_name_consent(), True)

_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types, True)
