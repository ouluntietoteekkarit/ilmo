from app import db


# MEMO: Must have same attribute names as BasicForm
class BasicModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    email = db.Column(db.String(128))
    privacy_consent = db.Column(db.Boolean())
    show_name_consent = db.Column(db.Boolean(), default=False)
    datetime = db.Column(db.DateTime())

    def get_firstname(self) -> str:
        return self.firstname

    def get_lastname(self) -> str:
        return self.lastname

    def get_email(self) -> str:
        return self.email

    def get_privacy_consent(self) -> bool:
        return self.privacy_consent

    def get_show_name_consent(self) -> bool:
        return self.show_name_consent

    def get_datetime(self):
        return self.datetime


class PhoneNumberColumn:
    phone_number = db.Column(db.String(32))

    def get_phone_number(self) -> str:
        return self.phone_number


# MEMO: Must have same attribute names as DepartureBusstopField
class DepartureBusstopColumn:
    departure_busstop = db.Column(db.String(64))

    def get_departure_busstop(self) -> str:
        return self.departure_busstop


# MEMO: Must have same attribute names as GuildField
class GuildColumn:
    guild_name = db.Column(db.String(16))

    def get_guild_name(self) -> str:
        return self.guild_name


# MEMO: Must have same attribute names as BindingRegistrationConsentField
class BindingRegistrationConsentColumn:
    binding_registration_consent = db.Column(db.Boolean())

    def get_binding_registration_consent(self) -> bool:
        return self.binding_registration_consent
