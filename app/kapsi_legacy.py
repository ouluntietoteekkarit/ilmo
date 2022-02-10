def kapsi_url(path):
       return 'https://ilmo.oty.fi/{}'.format(path)

msg = ["echo \"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
       "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
       "\n'Joukkueen nimi: ", str(form.teamname.data),
       "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
       str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
       str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
       str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email0.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)

msg = ["echo \"Hei", str(form.etunimi1.data), str(form.sukunimi1.data),
       "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
       "\n'Joukkueen nimi: ", str(form.teamname.data),
       "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
       str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
       str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
       str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email1.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)

msg = ["echo \"Hei", str(form.etunimi2.data), str(form.sukunimi2.data),
       "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
       "\n'Joukkueen nimi: ", str(form.teamname.data),
       "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
       str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
       str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
       str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email2.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)

msg = ["echo \"Hei", str(form.etunimi3.data), str(form.sukunimi3.data),
       "\n\nOlet ilmoittautunut pubivisaan. Syötit muun muassa seuraavia tietoja: ",
       "\n'Joukkueen nimi: ", str(form.teamname.data),
       "\n'Osallistujien nimet:\n", str(form.etunimi0.data), str(form.sukunimi0.data), "\n",
       str(form.etunimi1.data), str(form.sukunimi1.data), "\n",
       str(form.etunimi2.data), str(form.sukunimi2.data), "\n",
       str(form.etunimi3.data), str(form.sukunimi3.data), "\n",
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'pubivisa ilmoittautuminen' ", str(form.email3.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)





msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
       "\n\nOlet ilmoittautunut kortti- ja lautapeli-iltaan. Syötit seuraavia tietoja: ",
       "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
       "\nSähköposti: ", str(form.email.data),
       "\nPuhelinnumero: ", str(form.phone.data),
       "\nKilta: ", str(form.kilta.data),
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'kortti- ja lautapeli-ilta ilmoittautuminen' ",
       str(form.email.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)






msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
       "\n\nOlet ilmoittautunut slumberpartyyn. Syötit seuraavia tietoja: ",
       "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
       "\nSähköposti: ", str(form.email.data),
       "\nPuhelinnumero: ", str(form.phone.data),
       "\nKilta: ", str(form.kilta.data),
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'slumberparty ilmoittautuminen' ", str(form.email.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)





msg = ["echo \"Hei", str(form.etunimi0.data), str(form.sukunimi0.data),
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
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'pakopelipäivä ilmoittautuminen' ", str(form.email0.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)




msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
       "\n\nOlet jättänyt yhteystietosi hyvinvointi- ja etäopiskelukyselyn arvontaan. Syötit seuraavia tietoja: ",
       "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
       "\nSähköposti: ", str(form.email.data),
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'hyvinvointi- ja etäopiskelukysely' ", str(form.email.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)





msg = ["echo \"Hei", str(form.etunimi.data), str(form.sukunimi.data),
       "\n\nOlet ilmoittautunut fuksilauluiltaan. Syötit seuraavia tietoja: ",
       "\n'Nimi: ", str(form.etunimi.data), str(form.sukunimi.data),
       "\nSähköposti: ", str(form.email.data),
       "\n\nÄlä vastaa tähän sähköpostiin",
       "\n\nTerveisin: ropottilari\"",
       "|mail -aFrom:no-reply@oty.fi -s 'fuksilauluilta ilmoittautuminen' ", str(form.email.data)]

cmd = ' '.join(msg)
returned_value = os.system(cmd)