from django.urls import re_path, path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .views import  EmailGroupsListView, EmailGroupsDetailView, EmailGroupsCreateView,EmailGroupsUpdateView,EmailListView,EmailDetailView,EmailAttachmentDetailView,ResendEmailView
app_name = 'emails'
urlpatterns = [

    path('group', EmailGroupsListView.as_view(), name="list"),
    path('group/create', EmailGroupsCreateView.as_view(), name="create"),
    path('group/<int:pk>/update', EmailGroupsUpdateView.as_view(), name="update"),
    path('group/<int:pk>', EmailGroupsDetailView.as_view(), name="detail"),

    path('', EmailListView.as_view(), name="sent_list"),
    path('<uuid>', cache_page(60*10)(EmailDetailView.as_view()), name="email_detail"),
    path('resend/<uuid>', ResendEmailView.as_view(), name="resend"),

    path('attachment/<uuid>', EmailAttachmentDetailView.as_view(), name="attachment"),


]

