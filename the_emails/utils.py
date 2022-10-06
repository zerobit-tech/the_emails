
from templated_email import send_templated_mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# def emailx(template_name,recipients, from_email, context_data):
#     recipient_list = recipients
   

#     x = send_templated_mail(
#     create_link=True,
#     template_name=template_name,
#     from_email=from_email,  # super user email
#     recipient_list=recipient_list, # send to current acount and cc to super user
#     context=context_data,
#     # Optional:
#     # cc=['cc@example.com'],
#     # bcc=['bcc@example.com'],
#     # headers={'My-Custom-Header':'Custom Value'},
#     # template_prefix="my_emails/",
#     # template_suffix="email",
#     )
    
#     logger.debug(" email--send ",x)


"""
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If from_email is None, use the DEFAULT_FROM_EMAIL setting.
    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.

"""


def email(subject,template_name,recipients, context_data):
    subject = subject
    html_message = render_to_string(template_name, context_data)
    plain_message = strip_tags(html_message)
    
    mail.send_mail(subject, plain_message, None, recipients, html_message=html_message)