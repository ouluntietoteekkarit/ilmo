from datetime import datetime
from typing import List, Iterable, Tuple

from wtforms import RadioField, StringField
from wtforms.validators import DataRequired, length, Email

from app import db
from app.email import EmailRecipient, make_greet_line, make_signature_line
from .forms_util.form_controller import FormController, DataTableInfo, Event
from .forms_util.form_module import ModuleInfo, file_path_to_form_name
from .forms_util.forms import BasicForm, ShowNameConsentField, get_str_choices, RequiredIf
from .forms_util.models import BasicModel, basic_model_csv_map

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


@ShowNameConsentField()
class _Form(BasicForm):
    drink = RadioField('Juoma *', choices=get_str_choices(_get_drinks()), validators=[DataRequired()])
    liquor = RadioField('Viinakaato *', choices=get_str_choices(_get_liquors()), validators=[DataRequired()])
    wine = RadioField('Viini *', choices=get_str_choices(_get_wines()), validators=[DataRequired()])
    allergies = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])
    seating_preference = StringField('Pöytäseuratoive', validators=[length(max=50)])

    avec_firstname = StringField('Etunimi', validators=[length(max=50)])
    avec_lastname = StringField('Sukunimi', validators=[RequiredIf(other_field_name='avec_firstname'), length(max=50)])
    avec_email = StringField('Sähköposti', validators=[RequiredIf(other_field_name='avec_firstname'), Email(), length(max=100)])
    avec_drink = RadioField('Juoma', choices=get_str_choices(_get_drinks()), validators=[RequiredIf(other_field_name='avec_firstname')])
    avec_liquor = RadioField('Viinakaato', choices=get_str_choices(_get_liquors()), validators=[RequiredIf(other_field_name='avec_firstname')])
    avec_wine = RadioField('Viini', choices=get_str_choices(_get_wines()), validators=[RequiredIf(other_field_name='avec_firstname')])
    avec_allergies = StringField('Erityisruokavaliot/allergiat', validators=[length(max=200)])
    avec_seating_preference = StringField('Pöytäseuratoive', validators=[length(max=50)])

    def get_participant_count(self) -> int:
        return int(bool(self.firstname.data and self.lastname.data)) \
             + int(bool(self.avec_firstname.data and self.avec_lastname.data))


class _Model(BasicModel):
    __tablename__ = _form_name
    drink = db.Column(db.String(32))
    liquor = db.Column(db.String(32))
    wine = db.Column(db.String(32))
    allergies = db.Column(db.String(256))
    seating_preference = db.Column(db.String(50))

    avec_firstname = db.Column(db.String(64))
    avec_lastname = db.Column(db.String(64))
    avec_email = db.Column(db.String(128))
    avec_drink = db.Column(db.String(32))
    avec_liquor = db.Column(db.String(32))
    avec_wine = db.Column(db.String(32))
    avec_allergies = db.Column(db.String(256))
    avec_seating_preference = db.Column(db.String(50))

    def get_participant_count(self) -> int:
        return int(bool(self.firstname and self.lastname)) \
             + int(bool(self.avec_firstname and self.avec_lastname))


class _Controller(FormController):

    def _count_participants(self, entries) -> int:
        total_count = 0
        for m in entries:
            total_count += m.get_participant_count()

        return total_count

    # MEMO: "Evil" Covariant parameters
    def _find_from_entries(self, entries: Iterable[_Model], form: _Form) -> Tuple[bool, str]:
        def try_find(m: _Model, firstname: str, lastname: str, email: str):
            return ((m.get_firstname() == firstname and m.get_lastname() == lastname) or m.get_email() == email) or \
                   ((m.avec_firstname == firstname and m.avec_lastname == lastname) or m.avec_email == email)

        participant_firstname = form.get_firstname()
        participant_lastname = form.get_lastname()
        participant_email = form.get_email()
        avec_firstname = form.avec_firstname.data
        avec_lastname = form.avec_lastname.data
        avec_email = form.avec_email.data
        for entry in entries:
            if try_find(entry, participant_firstname, participant_lastname, participant_email):
                return True, ''
            if try_find(entry, avec_firstname, avec_lastname, avec_email):
                return True, 'Avecisi on jo ilmoittautunut'

        if participant_firstname == avec_firstname and participant_lastname == avec_lastname and participant_email == avec_email:
            return True, 'Et voi olla oma avecisi'

        return False, ''

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
                "\n\nJos tulee kysyttävää, voit olla sähköpostitse yhteydessä "
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

Jos tulee kysyttävää, voit olla sähköpostitse yhteydessä 
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
               datetime(2022, 3, 6, 23, 59, 59), 90, 40, _Form.asks_name_consent)
_module_info = ModuleInfo(_Controller, True, _form_name,
                          _event, _Form, _Model, _data_table_info)


# P U B L I C   M O D U L E   I N T E R F A C E   S T A R T
def get_module_info() -> ModuleInfo:
    return _module_info
# P U B L I C   M O D U L E   I N T E R F A C E   E N D
