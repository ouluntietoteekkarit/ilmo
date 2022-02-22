from datetime import datetime
from typing import List, Iterable

from wtforms import StringField
from wtforms.validators import DataRequired, length

from app import db
from app.email import EmailRecipient, make_greet_line
from .forms_util.form_controller import FormController, DataTableInfo, Event, Quota
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import get_str_choices, RequiredIf, get_quota_choices, BasicParticipantForm,\
    ParticipantFormBuilder, make_field_firstname, make_field_lastname, make_field_email, AttachableRadioField,\
    ATTRIBUTE_NAME_FIRSTNAME, make_field_quota, FormBuilder, make_field_required_participants,\
    make_field_optional_participants, make_field_privacy_consent, make_field_name_consent
from .forms_util.guilds import GUILD_OTIT, GUILD_PROSE, GUILD_COMMUNICA
from .forms_util.models import BasicModel, basic_model_csv_map, GuildColumn

_form_name = file_path_to_form_name(__file__)

_DRINK_ALCOHOLIC = 'Alkoholillinen'
_DRINK_BEER = 'Olut'
_DRINK_CIDER = 'Siideri'
_DRINK_NON_ALCOHOLIC = 'Alkoholiton'
_DRINK_RED_WINE = 'Punaviini'
_DRINK_WHITE_WINE = 'Valkoviini'


def _get_drinks() -> List[str]:
    return [
        _DRINK_BEER,
        _DRINK_CIDER,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_liquors() -> List[str]:
    return [
        _DRINK_ALCOHOLIC,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_wines() -> List[str]:
    return [
        _DRINK_RED_WINE,
        _DRINK_WHITE_WINE,
        _DRINK_NON_ALCOHOLIC
    ]


def _get_quotas() -> List[Quota]:
    return [
        Quota(GUILD_OTIT, 30, 10),
        Quota(GUILD_PROSE, 30, 10),
        Quota(GUILD_COMMUNICA, 30, 10),
    ]


class _BaseParticipant(BasicParticipantForm):
    allergies = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])
    seating_preference = StringField('Pöytäseuratoive', validators=[length(max=50)])

    def get_quota_name(self) -> str:
        return self.guild_name.data


def _make_field_drink(validators: Iterable):
    return AttachableRadioField('drink', 'Juoma *', validators, None, get_str_choices(_get_drinks()))


def _make_field_liquor(validators: Iterable):
    return AttachableRadioField('liquor', 'Viinakaato *', validators, None, get_str_choices(_get_liquors()))


def _make_field_wine(validators: Iterable):
    return AttachableRadioField('wine', 'Viini *', validators, None, get_str_choices(_get_wines()))


_Participant = ParticipantFormBuilder().add_fields([
    make_field_firstname([DataRequired()]),
    make_field_lastname([DataRequired()]),
    make_field_email([DataRequired()]),
    make_field_quota('Kilta *', get_quota_choices(_get_quotas()), [DataRequired()]),
    _make_field_drink([DataRequired()]),
    _make_field_liquor([DataRequired()]),
    _make_field_wine([DataRequired()])
]).build(_BaseParticipant)

_AvecParticipant = ParticipantFormBuilder().add_fields([
    make_field_firstname(),
    make_field_lastname([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)]),
    make_field_email([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)]),
    make_field_quota('Kilta *', get_quota_choices(_get_quotas()), [RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)]),
    _make_field_drink([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)]),
    _make_field_liquor([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)]),
    _make_field_wine([RequiredIf(other_field_name=ATTRIBUTE_NAME_FIRSTNAME)])
]).build(_BaseParticipant)

_Form = FormBuilder().add_fields([
    make_field_required_participants(_Participant, 1),
    make_field_optional_participants(_AvecParticipant, 1),
    make_field_name_consent(),
    make_field_privacy_consent()
]).build()


class _Model(BasicModel, GuildColumn):
    __tablename__ = _form_name
    drink = db.Column(db.String(32))
    liquor = db.Column(db.String(32))
    wine = db.Column(db.String(32))
    allergies = db.Column(db.String(256))
    seating_preference = db.Column(db.String(50))

    avec_firstname = db.Column(db.String(64))
    avec_lastname = db.Column(db.String(64))
    avec_email = db.Column(db.String(128))
    avec_guild_name = db.Column(db.String(16))
    avec_drink = db.Column(db.String(32))
    avec_liquor = db.Column(db.String(32))
    avec_wine = db.Column(db.String(32))
    avec_allergies = db.Column(db.String(256))
    avec_seating_preference = db.Column(db.String(50))

    def get_participant_count(self) -> int:
        return int(bool(self.firstname and self.lastname)) \
             + int(bool(self.avec_firstname and self.avec_lastname))

    def get_quota_counts(self) -> List[Quota]:
        return [
            Quota(self.guild_name, int(bool(self.firstname))),
            Quota(self.avec_guild_name, int(bool(self.avec_firstname)))
        ]


class _Controller(FormController):

    # MEMO: "Evil" Covariant parameter
    def _get_email_recipient(self, model: _Model) -> List[EmailRecipient]:
        """
        A method to get all email recipients to whom an email
        concerning current registration should be sent to.
         Can be overridden in inheriting classes to alter behaviour.
        """
        recipients = [
            EmailRecipient(model.get_firstname(), model.get_lastname(), model.get_email())
        ]
        if model.avec_firstname and model.avec_lastname:
            recipients.append(EmailRecipient(model.avec_firstname, model.avec_lastname, model.avec_email))
        return recipients

    # MEMO: "Evil" Covariant parameter
    def _get_email_msg(self, recipient: EmailRecipient, model: _Model, reserve: bool) -> str:
        if reserve:
            return ' '.join([
                make_greet_line(recipient),
                "\nOlet ilmoittautunut humanöörisitseille. Olet varasijalla.",
                "Jos sitseille jää syystä tai toisesta vapaita paikkoja, niin sinuun voidaan olla yhteydessä. ",
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä joensuu@otit.fi"
                "\n\nÄlä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."
            ])
        else:
            return ' '.join([
                make_greet_line(recipient),
                """\nOlet ilmoittautunut humanöörisitseille. Sitsit järjestetään Walhallassa 14.3. klo 18:00 alkaen.
                
Tässä vielä maksuohjeet:
Maksettava summa on 23€. 46€ jos osallistut avecin kanssa. Maksu tapahtuu tilisiirrolla
Communica ry:n tilille FI52 5741 3620 5641 27. Kirjoita viestikenttään oma nimesi, avecisi 
nimi ja \"humanöörisitsit\". Maksun eräpäivä on 14.3.2022.

Sitsien jatkoja varten mukaan OMPx2

Jos tulee kysyttävää, voit olla sähköpostitse yhteydessä joensuu@otit.fi
Älä vastaa tähän sähköpostiin, vastaus ei mene silloin mihinkään."""
            ])


_data_table_info = DataTableInfo(
    basic_model_csv_map() +
    [('drink', 'juoma'),
     ('liquor', 'viinakaato'),
     ('wine', 'viini'),
     ('allergies', 'erityisruokavaliot/allergiat'),
     ('seating_preference', 'pöytäseuratoive'),
     ('avec_firstname', 'avec etunimi'),
     ('avec_lastname', 'avec sukunimi'),
     ('avec_email', 'avec sähköposti',),
     ('avec_drink', 'avec juoma'),
     ('avec_liquor', 'avec viinakaato'),
     ('avec_wine', 'avec viini'),
     ('avec_allergies', 'avec erityisruokavaliot/allergiat'),
     ('avec_seating_preference', 'avec pöytäseuratoive')])
_event = Event('Humanöörisitsit', datetime(2021, 2, 21, 12, 00, 00),
               datetime(2022, 3, 6, 23, 59, 59), _get_quotas(), _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
