from django.forms import ModelForm
from .models import EmailGroups
import logging
logger = logging.getLogger('ilogger')

class EmailGroupsForm(ModelForm):
	class Meta:
		model = EmailGroups
		fields = ['group_name', 'email_id']