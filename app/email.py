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


def pubi_visa_mail_to(form, recipient):
    msg = ' '.join(["\"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
                    "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
                    "\n'Joukkueen nimi: ", str(form.teamname.data),
                    "\n'Osallistujien nimet:\n",
                    str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
                    str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
                    str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
                    str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "pubivisa ilmoittautuminen", recipient)


def pubi_visa_mail(form):
    pubi_visa_mail_to(form, str(form.email0.data))
    pubi_visa_mail_to(form, str(form.email1.data))
    pubi_visa_mail_to(form, str(form.email2.data))
    pubi_visa_mail_to(form, str(form.email3.data))


def peli_ilta_mail(form):
    msg = ' '.join(["\"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                    "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
                    "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                    "\nSähköposti: ", str(form.email.data),
                    "\nPuhelinnumero: ", str(form.phone.data),
                    "\nKilta: ", str(form.kilta.data),
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "kortti- ja lautapeli-ilta ilmoittautuminen", str(form.email.data))


def slumberparty_mail(form):
    msg = ' '.join(["\"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                    "\n\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
                    "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                    "\nSähköposti: ", str(form.email.data),
                    "\nPuhelinnumero: ", str(form.phone.data),
                    "\nKilta: ", str(form.kilta.data),
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "slumberparty ilmoittautuminen", str(form.email.data))


def pakopeli_mail(form):
    msg = ' '.join(["\"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
                    "\n\nOlet ilmoittautunut OTYn Pakopelipäivä tapahtumaan. Syötit seuraavia tietoja: ",
                    "\n'Nimi: ", str(form.etunimi0.data), str(form.sukunimi0.data),
                    "\nSähköposti: ", str(form.email0.data),
                    "\nPuhelinnumero: ", str(form.phone0.data),
                    "\nMuiden joukkuelaisten nimet: ", str(form.etunimi1.data), str(form.sukunimi1.data),
                    str(form.etunimi2.data), str(form.sukunimi2.data),
                    str(form.etunimi3.data), str(form.sukunimi3.data),
                    str(form.etunimi4.data), str(form.sukunimi4.data),
                    str(form.etunimi5.data), str(form.sukunimi5.data),
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "pakopelipäivä ilmoittautuminen", str(form.email0.data))


def hyvinvointi_mail(form):
    msg = ' '.join(["\"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                    "\n\nOlet jättänyt yhteystietosi hyvinvointi- ja etäopiskelukyselyn arvontaan. Syötit seuraavia tietoja: ",
                    "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                    "\nSähköposti: ", str(form.email.data),
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "hyvinvointi- ja etäopiskelukysely", str(form.email.data))


def fuksilaulu_mail(form):
    msg = ' '.join(["\"Hei", str(form.etunimi.data), str(form.sukunimi.data),
                    "\n\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
                    "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
                    "\nSähköposti: ", str(form.email.data),
                    "\n\nÄlä vastaa tähän sähköpostiin",
                    "\n\nTerveisin: ropottilari\""])
    send_email(msg, "fuksilauluilta ilmoittautuminen", str(form.email.data))

