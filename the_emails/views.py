from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.shortcuts import get_object_or_404,redirect
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, View
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

 
from the_system.text_choices import EmailStatus,EmailGroups

from the_user.initial_groups import CUSTOMER_CARE_SUPERVISER, CUSTOMER_CARE_REP, CUSTOMER_CARE_MANAGER
from the_user.mixin import OPTRequiredMixin,CCRRequiredMixin,AdminRequiredMixin

from .models import EmailGroups, Email, EmailAttachment
from .forms import EmailGroupsForm
from the_system.settings import get_page_size
 
# from .filters import BillingCycleFilter
import logging
logger = logging.getLogger('ilogger')
# Create your views here.
 
# ----------------------------------------------------------------
# 
# ---------------------------------------------------------------- 
class EmailGroupsListView(AdminRequiredMixin,ListView):
    model = EmailGroups
    paginate_by = get_page_size()
    #filterset_class = BillingCycleFilter
 
class EmailGroupsDetailView(AdminRequiredMixin,DetailView):
    model = EmailGroups
    
class EmailGroupsCreateView(AdminRequiredMixin,SuccessMessageMixin, CreateView):
	model = EmailGroups
	form_class = EmailGroupsForm
	success_message = _('Email group added successfully.')
 
class EmailGroupsUpdateView(AdminRequiredMixin,SuccessMessageMixin, UpdateView):
	model = EmailGroups
	form_class = EmailGroupsForm
	success_message = _('Email group updated successfully.')
 
# ----------------------------------------------------------------
# 
# ---------------------------------------------------------------- 
class EmailListView(CCRRequiredMixin,ListView):
    model = Email
    paginate_by = get_page_size()
    #filterset_class = BillingCycleFilter
    ordering = ['-pk']
class EmailDetailView(CCRRequiredMixin,DetailView):
    model = Email
    def get_object(self, queryset=None):
        return Email.objects.get(uuid=self.kwargs.get("uuid"))    

# ----------------------------------------------------------------
# 
# ---------------------------------------------------------------- 
 

class EmailAttachmentDetailView(CCRRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        user = request.user
        attachment_id = self.kwargs['uuid']
        attachment= get_object_or_404(EmailAttachment, uuid=attachment_id)  
        return HttpResponse(attachment.as_byte_stream().getvalue(), content_type=attachment.content_type)

# ----------------------------------------------------------------
# 
# ---------------------------------------------------------------- 
class ResendEmailView(CCRRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        user = request.user
        email_id = self.kwargs['uuid']
        email= get_object_or_404(Email, uuid=email_id)  
        
        if email.is_pending():
            messages.info(request, _('Email status is still pending. System will process it automatically'))
            return redirect(email.get_absolute_url())
        else:
            new_email =  email.resend()
            return redirect(new_email.get_absolute_url())