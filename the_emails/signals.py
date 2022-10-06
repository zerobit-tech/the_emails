from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Email
from the_system.utils import unique_slug_generator

# @receiver(pre_save,sender = Email)
# def slugify_now(sender,instance,**kwarg):
#     if instance.id is None:
#         instance.slug = unique_slug_generator(instance=instance, new_slug=slugify(str(instance.account)))
#     else:
#         pass