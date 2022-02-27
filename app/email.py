import base64
import shlex
import os
import html


_EMAIL_SENDER_BOT = 'no-reply@otit.fi'
_EMAIL_ENCODING = 'utf-8'


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
    # MEMO: Subject must use encoded word
    # MEMO: HTML escaping here prevents use of HTML layout in the email
    subject = _encode_word(subject, _EMAIL_ENCODING)
    content_type = 'text/html; charset={}'.format(_EMAIL_ENCODING)
    msg = html.escape(msg)
    cmd = "echo {} | mail  --content-type={} --append=From:{} --subject={} {}".format(
        shlex.quote(msg),
        shlex.quote(content_type),
        shlex.quote(_EMAIL_SENDER_BOT),
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


def _encode_word(data: str, encoding: str):
    # MEMO:
    #       https://en.wikipedia.org/wiki/MIME#Encoded-Word
    #       https://datatracker.ietf.org/doc/html/rfc2047
    data = data.encode(encoding)
    data = base64.b64encode(data)
    data = data.decode('ascii')
    return "=?{}?B?{}?=".format(encoding, data)
