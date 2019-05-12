from django.conf import settings

import smtplib
import random
import string
from user.mail_templates import get_validation_message
from core.models import ValidationToken


def send_email(mail_address, name, msg):
    # Send email
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_HOST_USER,
                    mail_address, msg.as_string())
    server.quit()


def token_generator():
    allowed_chars = ''.join((string.ascii_letters, string.digits))
    activation_code = ''.join(random.choice(allowed_chars) for _ in range(9))
    return activation_code


class ValidateEmail():

    def send_confirmation(self, mail_address, name):
        # Send email with confirmation token
        account_activation_token = token_generator()
        ValidationToken.objects.create(
            user_email=mail_address, token=account_activation_token)
        validation_link = 'http://localhost:8000/\
            api/user/activate_account/?email='
        validation_link += mail_address
        validation_link += '&token='
        validation_link += str(account_activation_token)
        send_email(
            'emanuelisc@gmail.com',
            name,
            get_validation_message(
                mail_address,
                name,
                validation_link,
                str(account_activation_token)
            )
        )


class ConfirmAnonReview():

    def send_confirmation(self, mail_address, name, review_id):
        # Send email with confirmation token
        account_activation_token = token_generator()
        ValidationToken.objects.create(
            user_email=mail_address, token=account_activation_token)
        validation_link = 'http://localhost:8000/\
            api/review/confirm_review/?email='
        validation_link += mail_address
        validation_link += '&token='
        validation_link += str(account_activation_token)
        validation_link += '&review='
        validation_link += str(review_id)
        send_email(
            'emanuelisc@gmail.com',
            name,
            get_validation_message(
                mail_address,
                name,
                validation_link,
                str(account_activation_token)
            )
        )
