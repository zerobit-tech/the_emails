 
from re import S
from io import BytesIO

from pathlib import Path
import uuid
from xhtml2pdf import pisa

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import mail
from django.utils import translation
from django.core.mail.message import (
    DEFAULT_ATTACHMENT_MIME_TYPE, BadHeaderError, EmailMessage,
    EmailMultiAlternatives, SafeMIMEMultipart, SafeMIMEText,
    forbid_multi_line_headers, make_msgid,
)

from django.utils import timezone
from django.conf import settings
from render_block import render_block_to_string, BlockNotFound

# Create your models here.
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from the_system.text_choices import EmailStatus,EmailGroups
from django.utils.translation import gettext_lazy as _
from the_system.text_choices import EmailStatus,EmailGroups
from the_system.utils.pdf_utils import template_to_pdf
from the_system.utils.file_utils import format_filename,get_template_name
from the_system.utils.template_utils import template_to_string
from the_system.signals import notify_user
from django.template.base import Template
from django.template.backends.django import Template
import traceback
import logging
logger = logging.getLogger('ilogger')
#----------------------------------------------------------------
#
#----------------------------------------------------------------

# for log reporting
class EmailGroups(models.Model):
    group_name  = models.CharField(max_length=25, choices=EmailGroups.choices)
    email_id = models.EmailField()
    class Meta:
        verbose_name_plural = "Email Groups"
        unique_together = [['group_name', 'email_id']]
    #----------------------------------------------------------------
    def save(self, *args, **kwargs):
        self.full_clean()
        self.group_name = self.group_name.upper()
        super().save(*args, **kwargs)

 #----------------------------------------------------------------
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('emails:list' )
 #----------------------------------------------------------------
  
    # this does not queue emails.
    @classmethod
    def send_mail(cls,group_name, subject, message, fail_silently=False, connection=None,
                html_message=None):

        group_emails = EmailGroups.objects.filter(group_name__iexact=group_name.upper())
        if not group_emails:
            return


        mail = EmailMultiAlternatives(
            '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject), message,
            settings.SERVER_EMAIL, [a.email_id for a in group_emails],
            connection=connection,
        )
        if html_message:
            mail.attach_alternative(html_message, 'text/html')
        mail.send(fail_silently=fail_silently)

#----------------------------------------------------------------
#
#----------------------------------------------------------------
class Email(models.Model):

    sender_ct = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True, null=True,
      
    )
    sender_id = models.PositiveIntegerField( blank=True, null=True,)

    sender = GenericForeignKey('sender_ct', 'sender_id')

    sub_sender_ct = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('sub sender'),
        blank=True, null=True,
        related_name="sub_emails"
      
    )
    sub_sender_id = models.PositiveIntegerField( blank=True, null=True,)

    sub_sender = GenericForeignKey('sub_sender_ct', 'sub_sender_id')

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    subject = models.TextField(verbose_name=_("Subject"))
    html_message = models.TextField(verbose_name=_("HTML Message"))
    plain_message = models.TextField(verbose_name=_("Plain Message"))
    template_name = models.TextField(verbose_name=_("Template Name"))

    status = models.CharField(max_length=1, choices=EmailStatus.choices, default=EmailStatus.PENDING, verbose_name=_("Email Status"))
    status_message = models.TextField( verbose_name=_("Status Message"))
    queued_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Queued Date"))
    sent_date = models.DateTimeField(null=True, blank=True) 
    copy_of = models.ForeignKey("self",null= True, related_name="copies", on_delete=models.SET_NULL, verbose_name=_("Copy of"))
    #----------------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.subject}:{self.sender}:{self.status}:{self.status_message}"


    def is_pending(self):
        return (self.status == str(EmailStatus.PENDING))
   #----------------------------------------------------------------

    def resend(self):
        new_email = Email.objects.create(
            sender = self.sender,
            subject = self.subject,
            html_message = self.html_message,
            plain_message = self.plain_message,
            template_name = self.template_name,
            copy_of = self
        )
        for recipient in self.get_recipients():
            EmailRecipients.objects.create(
                email = new_email,
                email_address = str(recipient)
            )
        for attachment in self.get_attachments():
            EmailAttachment.objects.create(
                email = new_email ,
                name = attachment.name,
                template_name = attachment.template_name,
                content = attachment.content,
                content_type =  attachment.content_type
            )

        #new_email.send_now()
        return new_email

    #----------------------------------------------------------------
    def send_now(self):
        try:
            email_to_send = mail.EmailMultiAlternatives(subject = self.subject,
                                            body = self.plain_message,
                                            from_email = None,
                                            to=self.get_recipients(),
                                            )

            email_to_send.attach_alternative(self.html_message, "text/html")
            result = BytesIO()

            for attachment in self.get_attachments():

                print(" ---- attachement ---" , attachment.template_name)
                try:
                    pisa.pisaDocument(BytesIO(attachment.content.encode("ISO-8859-1")), result)

                    email_to_send.attach(filename = attachment.name,
                    content=result.getvalue(),
                    mimetype = attachment.content_type
                    )
                except Exception as e:
                    logger.error(f"@admin: Error procssing attachment {attachment.template_name} to {self}: {e}")
                    raise e

            email_to_send.send()
            self.sent_date = timezone.localtime(timezone.now())
            self.status = EmailStatus.SENT
            notify_user.send(sender = None , recipient=self.sender.get_owner(), verb=_("New email"), action_object = self.sub_sender ,target=self.sender, description=self.subject )

        except Exception as e:
            self.status_message = str(e)
            self.status = EmailStatus.ERROR
             

        self.save()
    #----------------------------------------------------------------
    def get_recipients(self):
        recipients = list(self.recipients.all())
        return recipients
    #----------------------------------------------------------------
    def get_attachments(self):
        attachments = list(self.attachments.all())
        return attachments
    #----------------------------------------------------------------
    def get_absolute_url(self):
        from django.urls import reverse

        url_to_return = reverse('emails:email_detail', kwargs={'uuid' : self.uuid})
        try:
            if self.sender:
                return self.sender.get_sent_email_detail_url(self.pk) 
        except:
            pass
        return url_to_return

   

    #----------------------------------------------------------------
    def get_resend_url(self):
        from django.urls import reverse
        return reverse('emails:resend', kwargs={'uuid' : self.uuid})
    #----------------------------------------------------------------
    def _create_attachment(self, attachment,sender,context_data):

        if not attachment:
            return 

        attement_data = ''
        content_type = ""

        if sender:
            attement_data = template_to_string(sender.get_email_language(), attachment, context_data)  
            content_type='application/pdf'

        if not attement_data:
            attement_data  = render_to_string(attachment, context_data)
            content_type='application/pdf'

        try:
            attachment_name = render_block_to_string(attachment, "filename", context_data)
        except BlockNotFound as error:
                attachment_name = None

            
        name  = format_filename(attachment_name or f"{Path(attachment).stem}")

        name = f"{name}.pdf"

        EmailAttachment.objects.create(email=self,
                name=name,
                template_name = attachment,
                content = attement_data,
                content_type=content_type
        )

    #----------------------------------------------------------------
    def include_attachment(self, attach=[],sender=None, context_data={}):
        if isinstance(attach, (list, tuple)):
            for attement in attach:
                self._create_attachment(attement,sender,context_data)
        else:
            self._create_attachment(attach,sender,context_data)
         

    #----------------------------------------------------------------
    @classmethod
    def queue_email(cls,subject,template_name,context_data, recipients=[], sender=None, sub_sender=None,attach=[]):
        """
        template_name : can be a single name or a list
                        render_to_string can handle both

        sender need to implement: EmailSenderMixin
                        get_sent_email_detail_url()
                        get_email_language()

        """
        # TODO optimize it as render_to_string also using same logic
        #      maybe write a version of render_to_string

        template_name = get_template_name(template_name)
        
 
        if not template_name:
            return 

     

        try:
            subject_from_template = render_block_to_string(template_name, "subject", context_data)
        except BlockNotFound as error:
                subject_from_template = None

        email = Email(
            sender = sender,
            sub_sender = sub_sender,
            subject= subject_from_template or subject,
            template_name = template_name

            )
        
        email.save()

        if sender:
            email.html_message =  template_to_string(sender.get_email_language(),template_name, context_data)  
            for receipent in sender.get_email_recipients():
                email.recipients.create(email_address=receipent)  

        # if account is not given or account's template_to_string return empty string
        if not email.html_message:
            email.html_message  = render_to_string(template_name, context_data)
      

        
        email.plain_message = strip_tags(email.html_message)
         
                
        for recipient in recipients:
            email.recipients.create(email_address=recipient)


        email.include_attachment(attach=attach,sender=sender,context_data=context_data)
            
        email.save()

        #email.send_now()
        
        return email



    @classmethod
    def send(cls, id):
        try:
            email = Email.objects.get(pk=id)
            email.send_now()
        except Email.DoesNotExist:
            email = None
        


#----------------------------------------------------------------
#
#----------------------------------------------------------------
class EmailRecipients(models.Model):
    email = models.ForeignKey(Email ,on_delete=models.PROTECT, related_name="recipients")

    email_address = models.EmailField()

    def __str__(self) -> str:
        return f"{self.email_address}"


#----------------------------------------------------------------
#
#----------------------------------------------------------------
class EmailAttachment(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)    
    email = models.ForeignKey(Email ,on_delete=models.PROTECT, related_name="attachments")
    name = models.CharField(max_length=140, null=True, default="attachment")
    template_name = models.TextField(verbose_name=_("Template Name"))
    content = models.TextField(verbose_name=_("Content"))
    content_type = models.TextField(verbose_name=_("Content Type"))

    def __str__(self) -> str:
        return f"{self.name}"

    def as_byte_stream(self):
        result = BytesIO()
        pisa.pisaDocument(BytesIO(self.content.encode("ISO-8859-1")), result)
        return result
    #----------------------------------------------------------------
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('emails:attachment', kwargs={'uuid' : self.uuid})