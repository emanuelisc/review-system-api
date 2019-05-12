from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_validation_message(mail_address, name, link, code):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Sveiki prisijungę prie Atsiliepimų portalo!"
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = 'emanuelisc@gmail.com'

    text = "Sveiki!\n\nPatvirtinkite savo elektroninį paštą, \
        kad galėtumėte naudotis \
            visomis registruoto vartotojo galimybėmis\n\n"
    text += "Norėdami patvirtinti, \
        paspauskite toliau esančią nuorodą: \n" + link
    text += "\n\nJei negalite paspausti nuorodos, \
        nukopijuokite žemiau esantį kodą:\n" + code
    text += "\n\nDžiaugiamės, kad prisijungėte prie mūsų. \
        Tikimės savo atsiliepimų pagalba padėsite kitiems \
            vartotojams atsirinkti kokybiškas paslaugas\n"
    text += "\nPagarbiai\nAtsiliepimai.tk komanda."
    part1 = MIMEText(text, 'plain')
    # part2 = MIMEText(html, 'html')
    msg.attach(part1)
    # msg.attach(part2)
    return msg


def get_anon_review_message(mail_address, name, link, code, password):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Naujas atsiliepimas portale!"
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = 'emanuelisc@gmail.com'

    text = "Sveiki!\n\nPatvirtinkite savo elektroninį paštą,\
         kad jūsų atsiliepimas būtų patvirtintas ir paskelbtas.\n\n"
    text += "Norėdami patvirtinti, \
        paspauskite toliau esančią nuorodą: \n" + link
    text += "\n\nJei negalite paspausti nuorodos,\
         nukopijuokite žemiau esantį kodą:\n" + code
    text += "\n\nJei vėliau norėsite panaikinti\
         arba redaguoti atsiliepimą, prisijunkite \
             prie sistemos toliau nurodytais duomenimis:\n"
    text += "Elektroninis paštas: " + mail_address
    text += "\nSlaptažodis: " + password
    text += "\n\nPagarbiai\nAtsiliepimai.tk komanda."
    part1 = MIMEText(text, 'plain')
    # part2 = MIMEText(html, 'html')
    msg.attach(part1)
    # msg.attach(part2)
    return msg
