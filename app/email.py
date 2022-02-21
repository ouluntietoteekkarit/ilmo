import shlex
import os


_EMAIL_SENDER_BOT = 'no-reply@otit.fi'


class EmailRecipient:

    def __init__(self, firstname: str, lastname: str, email_address: str):
        self._firstname = firstname
        self._lastname = lastname
        self._email_address = email_address

    def get_email_address(self) -> str:
        return self._email_address

    def get_firstname(self) -> str:
        return self._firstname

    def get_lastname(self) -> str:
        return self._lastname


def kapsi_url(path: str):
    return 'https://ilmo.oty.fi/{}'.format(path)


def send_email(msg: str, subject: str, recipient: EmailRecipient):
    cmd = "echo {} | mail -aFrom:{} -s {} {}".format(
        shlex.quote(msg),
        _EMAIL_SENDER_BOT,
        shlex.quote(subject),
        shlex.quote(recipient.get_email_address())
    )
    os.system(cmd)


def make_greet_line(recipient: EmailRecipient) -> str:
    return "Hei " + make_fullname(recipient.get_firstname(), recipient.get_lastname()) + "\n\n"


def make_signature_line() -> str:
    return """Älä vastaa tähän sähköpostiin

Terveisin: ropottilari"""


def make_fullname(firstname: str, lastname: str) -> str:
    return "{} {}".format(firstname, lastname)


def make_fullname_line(firstname: str, lastname: str) -> str:
    return make_fullname(firstname, lastname) + "\n"
