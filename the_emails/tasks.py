from __future__ import absolute_import, unicode_literals
import random
from the_system.services import registered_services
 
from django.utils import timezone
from django.db.models import Q
from django.db.models import F
 

from the_system.text_choices import TransactionTypes

 
from .models import Email 
from the_system.text_choices import EmailStatus
from the_system.locks import lock_object
import logging
logger = logging.getLogger('ilogger')


def send_pending_email():
    logger.debug(f" =========START======> SENDING PENDING EMAILS <====================")

    emails_to_send = Email.objects.filter(status=EmailStatus.PENDING).all()
    for email in emails_to_send:
        if lock_object(str(email),extra_id=send_pending_email):
            email.send_now()
            
    logger.debug(f" =========END======> SENDING PENDING EMAILS <====================")


celery_app = registered_services.get("celery_app",None)


if celery_app:
   send_pending_email= celery_app.task(name="SEND PENDING EMAILS")(send_pending_email)