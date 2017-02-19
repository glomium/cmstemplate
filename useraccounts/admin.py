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
    readonly_fields=('email',)
    list_display = BaseUserAdmin.list_display + ('is_valid',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_primary', 'is_valid', 'validated', 'updated', 'created')
    list_filter = ('is_primary', 'is_valid')
