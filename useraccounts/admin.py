#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Email
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields=('email', 'is_valid')
    list_display = BaseUserAdmin.list_display + ('is_valid',)
    actions = ["make_email_invalid"]

    def make_email_invalid(self, request, queryset):
        rows = 0
        for obj in queryset:
            obj.make_email_invalid()
            rows += 1

        if rows == 1:
            self.message_user(request, "One useraccount status was successfully updated to invalid email address.")
        else:
            self.message_user(request, "%s useraccounts were successfully updated to invalid email addresses status." % rows)

    make_email_invalid.short_description = "Update email address to invalid"


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_primary', 'is_valid', 'validated', 'updated', 'created')
    list_filter = ('is_primary', 'is_valid')
