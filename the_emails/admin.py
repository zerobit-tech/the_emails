from django.contrib import admin
from .models import Email, EmailGroups
# Register your models here.

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("sender","subject")


@admin.register(EmailGroups)
class EmailGroupsAdmin(admin.ModelAdmin):
    list_display = ("group_name","email_id")