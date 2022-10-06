from copy import copy

from django.views import debug
from django.utils import log
from django.conf import settings
from django import template

 


TECHNICAL_500_TEMPLATE = """ """ # # custom template here, copy the original and make adjustments

TECHNICAL_500_TEXT_TEMPLATE = """ """ # # custom template here, copy the original and make adjustments

class CustomExceptionReporter(debug.ExceptionReporter):
    def get_traceback_html(self):
        t = debug.DEBUG_ENGINE.from_string(TECHNICAL_500_TEMPLATE)
        c = template.Context(self.get_traceback_data(), use_l10n=False)
        return t.render(c)

    def get_traceback_text(self):
        t = debug.DEBUG_ENGINE.from_string(TECHNICAL_500_TEXT_TEMPLATE)
        c = template.Context(self.get_traceback_data(), autoescape=False, use_l10n=False)
        return t.render(c)

class CustomAdminEmailHandler(log.AdminEmailHandler):
    def emit(self, record):
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
        subject = self.format_subject(subject)

        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = CustomExceptionReporter(request, is_email=True, *exc_info)
        message = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())
        html_message = reporter.get_traceback_html() if self.include_html else None
        self.send_mail(subject, message, fail_silently=True, html_message=html_message)



class CustomEmailToGroupHandler(log.AdminEmailHandler):
    def emit(self, record):
        from .models import EmailGroups
        # return if email_group is not defined
        if not hasattr(record,"email_group_name"):
            return
        
        if not record.email_group_name:
            return 


        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None

        full_message = record.getMessage().split(":")
        new_subject = full_message[1] if len(full_message)>1 else subject


        subject = self.format_subject(new_subject)

        no_exc_record = copy(record)

 

        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = CustomExceptionReporter(request, is_email=True, *exc_info)
        
        message = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())

        html_message = reporter.get_traceback_html() if self.include_html else None
        EmailGroups.send_mail(record.email_group_name, subject, message, fail_silently=True, html_message=html_message)