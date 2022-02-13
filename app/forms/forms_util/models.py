from app import db


class BasicModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    etunimi = db.Column(db.String(64))
    sukunimi = db.Column(db.String(64))
    email = db.Column(db.String(128))

    def get_firstname(self) -> str:
        return self.etunimi

    def get_lastname(self) -> str:
        return self.sukunimi

    def get_email(self) -> str:
        return self.email


class ShowNameConsentMixin:
    show_name_consent = db.Column(db.Boolean())

    def get_show_name_consent(self) -> bool:
        return self.show_name_consent


class PrivacyStatementMixin:
    privacy_consent = db.Column(db.Boolean())

    def get_privacy_consent(self) -> bool:
        return self.privacy_consent
