import shlex
import os


_EMAIL_SENDER_BOT = 'no-reply@otitkakspistenolla.oulu.fi'

def kapsi_url(path: str):
    return 'https://ilmo.oty.fi/{}'.format(path)


def send_email(msg: str, subject: str, recipient: str):
    cmd = "echo {} | mail -aFrom:{} -s {} {}".format(
        shlex.quote(msg),
        _EMAIL_SENDER_BOT,
        shlex.quote(subject),
        shlex.quote(recipient)
    )
    os.system(cmd)

