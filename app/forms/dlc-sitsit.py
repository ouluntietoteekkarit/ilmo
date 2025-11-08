from datetime import datetime
from typing import List, Union

from wtforms.validators import InputRequired, NumberRange, Optional, Email
from typing import Any, Type, TYPE_CHECKING, Iterable, Tuple, Dict, Collection
from app.email import make_greet_line
from app.form_lib.common_attributes import make_attribute_firstname, make_attribute_lastname, make_attribute_email, \
    make_attribute_allergies, make_attribute_quota, make_attribute_name_consent, make_attribute_privacy_consent, \
    make_attribute_binding_registration_consent
from app.form_lib.drinks import make_attribute_usual_sitsi_drink, make_attribute_usual_sitsi_wine, \
    make_attribute_usual_sitsi_liquor, make_enum_usual_sitsi_drink, make_enum_usual_sitsi_liquor, \
    make_enum_usual_sitsi_wine
from app.form_lib.form_controller import FormController
from app.form_lib.event import Event
from app.form_lib.lib import BaseParticipant
from app.form_lib.quota import Quota
from app.form_lib.form_module import ModuleInfo, make_form_name
from app.form_lib.util import make_types, choices_to_enum, get_quota_choices
from app.form_lib.models import RegistrationModel
from app.form_lib.lib import StringAttribute, EnumAttribute, RadioButtonAttribute, IntAttribute
from app.form_lib.forms import RegistrationForm

# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D

class _Controller(FormController):

    def _get_email_msg(self, recipient: BaseParticipant, model: RegistrationModel, reserve: bool) -> str:

        s = make_greet_line(recipient) + "Olet ilmoittautunut OTiTin DLC-sitseille."

        if reserve:
            s += "\nOlet varasijalla. Jos paikkoja vapautuu, niin sinuun voidaan olla yhteydessä. Säilytä maksutiedot varalta."

        s += "\n\nTilauksesi yhteenveto:\n"
        kokonaishinta = 10.0

        s += f"Seuratoive: {recipient.get_poytaseura()}\n"
        
        # ---- RUOKAVALINNAT ----
        s += "\nTarjoilut:\n"

        ruokavalinta = recipient.get_ruoka()
        if ruokavalinta:
            s += f"• Ruoka: {ruokavalinta}, Allergiat: {recipient.get_allergies()}\n"
            kokonaishinta += self._extract_price(ruokavalinta)

        jalkiruoka = recipient.get_jalkiruoka()
        if jalkiruoka:
            s += f"• Jälkiruoka: {jalkiruoka}\n"
            kokonaishinta += self._extract_price(jalkiruoka)

        lasy = recipient.get_lasy()
        if lasy:
            s += f"• Läsy: {lasy}\n"
            kokonaishinta += self._extract_price(lasy)

        miedot = recipient.get_miedot()
        if miedot:
            s += f"• Miedot: {miedot}, Toive: {recipient.get_mietotoive()}\n"
            kokonaishinta += self._extract_price(miedot)

        kaadot = recipient.get_kaadot()
        if kaadot:
            s += f"• Kaadot: {kaadot}\n"
            kokonaishinta += self._extract_price(kaadot)

        kahviavec = recipient.get_kahviavec()
        if kahviavec:
            s += f"• Kahviavec: {kahviavec}\n"
            kokonaishinta += self._extract_price(kahviavec)

        ruokajuoma = recipient.get_ruokajuoma()
        if ruokajuoma:
            s += f"• Ruokajuoma: {ruokajuoma}, Toive: {recipient.get_ruokajuomatoive()}\n"
            kokonaishinta += self._extract_price(ruokajuoma)

        # ---- DLC-LISÄT ----
        s += "\nOstetut DLC:t:\n"

        if recipient.get_ruusuDLC() == "Kyllä":
            s += "• Vessel of Ruusu – 50 €\n"
            kokonaishinta += 50
        if recipient.get_valkokangasDLC() == "Kyllä":
            s += "• Screen of Wonders – 10 €\n"
            kokonaishinta += 10
        if recipient.get_pukukoodiDLC() == "Kyllä":
            s += f"• Sitsi Armor Pack – 20 € (Toive: {recipient.get_pukukoodi()})\n"
            kokonaishinta += 20
        if recipient.get_raffleDLC():
            s += f"• Loot Box – {recipient.get_raffleDLC()} x 1€\n"
            kokonaishinta += recipient.get_raffleDLC()
        if recipient.get_titanicDLC() == "Kyllä":
            s += "• Ultimate Thirst Edition – 50 €\n"
            kokonaishinta += 50
        if recipient.get_pukukoodi2DLC() == "Kyllä":
            s += f"• Workhorse Armor Pack – 10 € (Toive: {recipient.get_pukukoodi2()})\n"
            kokonaishinta += 10

        # ---- LOPPUTIEDOT ----
        s += "\nMaksuohjeet:\n"
        s += "Saaja: Oulun Tietoteekkarit ry\n"
        s += "Tilinumero: FI03 4744 3020 0116 87\n"
        s += f"Summa: {kokonaishinta:.2f} €\n"
        s += "Viesti: Oma Nimi + DLC-sitsit\n"
        s += "Eräpäivä: 13.12.2025\n"

        s += "\n\nJos tulee kysyttävää, ota yhteyttä joensuu@otit.fi. Älä vastaa tähän sähköpostiin, se ei mene minnekään!"
            
        return s

    @staticmethod
    def _extract_price(label: str) -> float:
        """Etsii hinnan merkkijonosta kuten 'Roiskeläppä 2.00€'."""
        import re
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*€", label)
        return float(match.group(1).replace(',', '.')) if match else 0.0
    
    def _find_from_entries(self, entries: Iterable[RegistrationModel], form: RegistrationForm) -> Tuple[bool, str]:
        participants = list(form.get_required_participants()) + list(form.get_optional_participants())
       
        counts = {
            "ruusu": 0,
            "valkokangas": 0,
            "pukukoodi": 0,
            "raffle": 0,
            "titanic": 0,
            "pukukoodi2": 0
        }
        
        registered_counts = {
            "ruusu": 0,
            "valkokangas": 0,
            "pukukoodi": 0,
            "raffle": 0,
            "titanic": 0,
            "pukukoodi2": 0
        }

        max_counts = {
            "ruusu": 1,
            "valkokangas": 1,
            "pukukoodi": 1,
            "raffle": 5 * 64,
            "titanic": 1,
            "pukukoodi2": 1
        }

        for p in participants:
            if p.get_ruusuDLC() == "Kyllä":
                counts["ruusu"] += 1
            if p.get_valkokangasDLC() == "Kyllä":
                counts["valkokangas"] += 1
            if p.get_pukukoodiDLC() == "Kyllä":
                counts["pukukoodi"] += 1
            if p.get_raffleDLC() == "Kyllä":
                counts["raffle"] += 1
            if p.get_titanicDLC() == "Kyllä":
                counts["titanic"] += 1
            if p.get_pukukoodi2DLC() == "Kyllä":
                counts["pukukoodi2"] += 1
            
        for m in entries:
            registered_participants = list(m.get_required_participants()) + list(m.get_optional_participants())
            for p in registered_participants:
                if p.get_ruusuDLC() == "Kyllä":
                    registered_counts["ruusu"] += 1
                if p.get_valkokangasDLC() == "Kyllä":
                    registered_counts["valkokangas"] += 1
                if p.get_pukukoodiDLC() == "Kyllä":
                    registered_counts["pukukoodi"] += 1
                if p.get_raffleDLC() == "Kyllä":
                    registered_counts["raffle"] += 1
                if p.get_titanicDLC() == "Kyllä":
                    registered_counts["titanic"] += 1
                if p.get_pukukoodi2DLC() == "Kyllä":
                    registered_counts["pukukoodi2"] += 1

        for participant in participants:
            firstname = participant.get_firstname()
            lastname = participant.get_lastname()
            email = participant.get_email()

            for m in entries:
                registered_participants = list(m.get_required_participants()) + list(m.get_optional_participants())
                for p in registered_participants:
                    if self._matching_identity(p.get_firstname(), firstname,
                                               p.get_lastname(), lastname,
                                               p.get_email(), email):
                        return True, '{} {} on jo ilmoittautunut.'.format(firstname, lastname)

        if counts["ruusu"] and registered_counts["ruusu"] >= max_counts["ruusu"]:
            return True, 'DLC on myyty loppuun'
        if counts["valkokangas"] and registered_counts["valkokangas"] >= max_counts["valkokangas"]:
            return True, 'DLC on myyty loppuun'
        if counts["pukukoodi"] and registered_counts["pukukoodi"] >= max_counts["pukukoodi"]:
            return True, 'DLC on myyty loppuun'
        if counts["raffle"] and registered_counts["raffle"] >= max_counts["raffle"]:
            return True, 'DLC on myyty loppuun'
        if counts["titanic"] and registered_counts["titanic"] >= max_counts["titanic"]:
            return True, 'DLC on myyty loppuun'
        if counts["pukukoodi2"] and registered_counts["pukukoodi2"] >= max_counts["pukukoodi2"]:
            return True, 'DLC on myyty loppuun'
                     
        return False, ''

_form_name = make_form_name(__file__)

def _get_quotas(registration_start: datetime, registration_end: datetime) -> List[Quota]:
    return [
        Quota('OTiT',   64,   999,  registration_start, registration_end),
    ]


_registration_start = datetime(2025, 11, 11, 12, 0, 0)
_registration_end = datetime(2026, 11, 30, 23, 59, 59)
_quotas = _get_quotas(_registration_start, _registration_end)

_QuotaEnum = choices_to_enum(_form_name, 'quota', get_quota_choices(_quotas))

"""
Tarjoilut valinnat
"""
_RuokaEnum = choices_to_enum(_form_name, 'ruoka', ["N/A 0.00€", "Roiskeläppä 2.00€", "Catering 7.00€"])
_JalkiruokaEnum = choices_to_enum(_form_name, 'jälkiruoka', ["Kahvi + maito 0.00€", "Pulla kahvit 0.50€"])
_LasyEnum = choices_to_enum(_form_name, 'läsy', ["N/A 0.00€", "Läsy 0.50€"])
_MiedotEnum = choices_to_enum(_form_name, 'miedot', ["N/A 0.00€", "Perus sitsijuoma 3.00€"])
_KaadotEnum = choices_to_enum(_form_name, 'kaadot', ["N/A 0.00€", "Maistuu maistuu 1.50€"])
_KahviavecEnum = choices_to_enum(_form_name, 'kahviavec', ["N/A 0.00€", "Maistuu maistuu 1.50€"])
_RuokajuomaEnum = choices_to_enum(_form_name, 'ruokajuoma', ["N/A 0.00€", "DIY-tier 1.00€", "Normi-tier 2.00€"])

"""
DLC - valinnat
"""
_RuusuDLC = choices_to_enum(_form_name, 'ruusu DLC', ["Ei", "Kyllä"])
_ValkokangasDLC = choices_to_enum(_form_name, 'valkokangas DLC' , ["Ei", "Kyllä"])
_PukukoodiDLC = choices_to_enum(_form_name, 'pukukoodi DLC', ["Ei", "Kyllä"])
_TitanicDLC = choices_to_enum(_form_name, 'titanic DLC', ["Ei", "Kyllä"])
_PukukoodiDLC2 = choices_to_enum(_form_name, 'työvoima pukukoodi', ["Ei", "Kyllä"])

participant_attributes = [


make_attribute_quota(_QuotaEnum, validators=[InputRequired()]),
    StringAttribute('firstname', 'Etunimi', 'Etunimi', 50, **{"validators": [InputRequired()]}),
    StringAttribute('lastname', 'Sukunimi', 'Sukunimi', 50, **{"validators": [InputRequired()]}),
    StringAttribute('email', 'Sähköposti', 'Sähköposti', 50, **{"validators": [Email(), InputRequired()]}),
    StringAttribute("poytaseura", "Pöytäseuratoive", "Pöytäseuratoive", 60),
    # Tarjoilut
    RadioButtonAttribute('ruoka', 'Ruoka', 'Ruoka', _RuokaEnum, 0, **{"choices":_RuokaEnum, "validators":[InputRequired()]}),
    RadioButtonAttribute('jalkiruoka', 'Jälkiruoka', 'JälkiRuoka', _JalkiruokaEnum, 0, **{"choices":_JalkiruokaEnum, "validators":[InputRequired()]}),
    RadioButtonAttribute('kahviavec', 'Kahviavec', 'Kahviavec', _KahviavecEnum, 0, **{"choices":_KahviavecEnum, "validators":[InputRequired()]}),
    RadioButtonAttribute('lasy', 'Läsy', 'Läsy', _LasyEnum, 0, **{"choices":_LasyEnum, "validators":[InputRequired()]}),
    RadioButtonAttribute('miedot', 'Miedot', 'Miedot', _MiedotEnum, 0, **{"choices":_MiedotEnum, "validators":[InputRequired()]}),
    StringAttribute("mietotoive", "Juomatoive", "Juomatoive", 60),
    RadioButtonAttribute('kaadot', 'Kaadot', 'Kaadot', _KaadotEnum, 0, **{"choices":_KaadotEnum, "validators":[InputRequired()]}),
    RadioButtonAttribute('ruokajuoma', 'Ruokajuoma', 'Ruokajuoma', _RuokajuomaEnum, 0, **{"choices":_JalkiruokaEnum, "validators":[InputRequired()]}),
    StringAttribute("ruokajuomatoive", "Ruokajuomatoive", "Juomatoive", 60),
    StringAttribute('allergies', 'Erityisruokavaliot tai allergiat', 'Erityisruokavaliot', 200),
    # DLC
    RadioButtonAttribute('ruusuDLC', 'Ruusu-DLC', 'Ruusu-DLC', _RuusuDLC, 0, **{"choices":_RuusuDLC, "validators":[InputRequired()]}),
    RadioButtonAttribute('valkokangasDLC', 'Valkokangas-DLC', 'Valkokangas-DLC', _ValkokangasDLC, 0, **{"choices":_ValkokangasDLC, "validators":[InputRequired()]}),
    RadioButtonAttribute('pukukoodiDLC', 'Pukukoodi-DLC', 'Pukukoodi-DLC', _PukukoodiDLC, 0, **{"choices":_PukukoodiDLC, "validators":[InputRequired()]}),
    StringAttribute('pukukoodi', 'Sitsien pukukoodi', 'Sitsien pukukoodi', 200),
    RadioButtonAttribute('pukukoodi2DLC', 'Työvoiman pukukoodi -DLC', 'Työvoiman Pukukoodi -DLC', _PukukoodiDLC2, 0, **{"choices":_PukukoodiDLC2, "validators":[InputRequired()]}),
    StringAttribute('pukukoodi2', 'Työvoiman pukukoodi', 'Työvoiman pukukoodi', 200),
    IntAttribute('raffleDLC', 'Raffle-DLC', 'Raffle-DLC', **{"validators":[Optional(), NumberRange(min=0, max=5, message="Max 5")]}),
    RadioButtonAttribute('titanicDLC', 'Titanikki-DLC', 'Titanikki-DLC', _TitanicDLC, 0, **{"choices":_TitanicDLC, "validators":[InputRequired()]})
]

optional_participant_attributes = []
other_attributes = [
    make_attribute_name_consent(),
    make_attribute_privacy_consent("", validators=[InputRequired()]),
    make_attribute_binding_registration_consent("", validators=[InputRequired()])
]

_types = make_types(participant_attributes, [], other_attributes, 1, 0, _form_name)

_event = Event('DLC-sitsit', _registration_start, _registration_end, _quotas, _types.asks_name_consent(), hide_title=True)
_module_info = ModuleInfo(_Controller, True, _form_name, _event, _types)

