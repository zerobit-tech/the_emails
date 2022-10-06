from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from .models import Email
from the_system.models import BaseModel
class EmailSenderMixinModel(BaseModel):

    emails = GenericRelation(Email,object_id_field='sender_id' ,content_type_field='sender_ct')

    def get_email_language(self):
        first_lang,_= settings.LANGUAGES[0]
        return first_lang

  

    class Meta:
        abstract = True


class EmailSubSenderMixinModel(BaseModel):

    sub_emails = GenericRelation(Email,object_id_field='sub_sender_id' ,content_type_field='sub_sender_ct')

    def get_email_language(self):
        first_lang,_= settings.LANGUAGES[0]
        return first_lang

   

    class Meta:
        abstract = True