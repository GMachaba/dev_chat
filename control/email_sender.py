import logging
from django.core.mail import send_mail
from dev_chat.settings import EMAIL_HOST_USER, EMAIL_HOST, EMAIL_HOST_PASSWORD
import smtplib

logger = logging.getLogger(__name__)


def send_email(subject, message, recipient):
    try:
        send_mail(subject, message, EMAIL_HOST_USER, recipient, fail_silently=False)
        return True
    except:
        return False