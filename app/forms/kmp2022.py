from datetime import datetime
from typing import List

from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, length, DataRequired

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_controller import FormController, FormContext, DataTableInfo, Event, EventRegistrations, Quota
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import BasicForm, get_str_choices, GuildField, get_quota_choices, RequiredIfValue, \
    DepartureBusstopField, ShowNameConsentField
from .forms_util.guilds import GUILD_SIK, GUILD_OTIT
from .forms_util.models import BasicModel, basic_model_csv_map, DepartureBusstopColumn, departure_busstop_csv_map

_form_name = file_path_to_form_name(__file__)


_QUOTA_WITH_ACCOMODATION = GUILD_OTIT + ' (majoituksella)'
_QUOTA_WITHOUT_ACCOMICATION = GUILD_SIK + ' (ei majoitusta)'


_DEPARTURE_BUS_STOP_UNI = 'Yliopisto (X-oven edestä)'
_DEPARTURE_BUS_STOP_MERIKOSKI = 'Tuira (Merikoskenkadun bussipysäkki)'
_DEPARTURE_BUS_STATION = 'Keskusta (Linja-autoasema)'


_ROOM_COMPOSITION_SAME_SEX = 'Samaa sukupuolta'
_ROOM_COMPOSITION_NO_PREFERENCE = 'Ei väliä'


def _get_sexes() -> List[str]:
    return [
        '',
        'Mies',
        'Nainen',
        'Muu'
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(_QUOTA_WITH_ACCOMODATION, 42, 15),
        Quota(_QUOTA_WITHOUT_ACCOMICATION, 13, 5)
    ]


def _get_departure_stops() -> List[str]:
    return [
        _DEPARTURE_BUS_STOP_UNI,
        _DEPARTURE_BUS_STOP_MERIKOSKI,
        _DEPARTURE_BUS_STATION
    ]


def _get_room_sex_options() -> List[str]:
    return [
        '',
        _ROOM_COMPOSITION_SAME_SEX,
        _ROOM_COMPOSITION_NO_PREFERENCE
    ]

@ShowNameConsentField()
@DepartureBusstopField(get_str_choices(_get_departure_stops()))
class _Form(BasicForm):
    quota = SelectField('Kiintiö *', choices=get_quota_choices(_get_quotas()), validators=[InputRequired()])
    roommate_preference = StringField('Huonekaveri toiveet (max 2)', validators=[
        length(max=100),
        RequiredIfValue(other_field_name='quota', value=_QUOTA_WITH_ACCOMODATION)])
    room_sex_composition = SelectField(
        'Haluatko majoittua samaa sukupuolta olevien kanssa?',
        choices=get_str_choices(_get_room_sex_options()), validators=[])
    sex = SelectField('Sukupuoli', choices=get_str_choices(_get_sexes()), validators=[
        RequiredIfValue(other_field_name='room_sex_composition', value=_ROOM_COMPOSITION_SAME_SEX)])
    allergies = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])

    def get_quota_counts(self) -> List[Quota]:
        return [Quota(self.quota.data, 1)]


class _Model(BasicModel, DepartureBusstopColumn):
    __tablename__ = _form_name
    quota = db.Column(db.String(64))
    roommate_preference = db.Column(db.String(100))
    room_sex_composition = db.Column(db.String(24))
    sex = db.Column(db.String(16))
    allergies = db.Column(db.String(200))


class _Controller(FormController):
    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        if reserve:
            return """{}Olet ilmoittautunut OTiTin ja SIKin KMP:lle. Olet varasijalla. Jos KMP:lle jää jostain syystä vapaita
paikkoja, sinuun voidaan olla yhteydessä.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))
        else:
            return """{}Ole ilmoittautunut OTiTin ja SIKin KMP:lle. KMP järjestetään 18. - 20.3. Tampereella.

Tässä vielä maksuohjeet:
OTiT-laisille summa on 60€. SIKkiläisille summa 35€. Osallistumismaksu maksetaan tilille 
FI03 4744 3020 0116 87. Maksun saajan nimi: Oulun Tietoteekkarit ry. Viestiksi KMP + oma nimi.

Jos tulee kysyttävää voit olla sähköpostitse yhteydessä kulttuuriministeri@otit.fi.

Älä vastaa tähän sähköpostiin. Viesti ei mene mihinkään. """.format(make_greet_line(recipient))


_data_table_info = DataTableInfo(
    basic_model_csv_map() +
    departure_busstop_csv_map() +
    [('quota', 'kiintiö'),
     ('roommate_preference', 'huonekaveri toiveet'),
     ('room_sex_composition', 'huonekaverien sukupuoli'),
     ('sex', 'sukupuoli'),
     ('allergies', 'erikoisruokavaliot')]
)
_event = Event('OTiT KMP', datetime(2021, 2, 25, 13, 37, 00),
               datetime(2022, 3, 10, 0, 0, 0), _get_quotas(), _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
