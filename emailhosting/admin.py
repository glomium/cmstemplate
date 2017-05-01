#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.messages import constants as messages
from django.utils.translation import ugettext_lazy as _

from .models import Domain
from .models import Account
from .models import Address
from .forms import HiddenPasswordForm


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'accept_mail')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'quota', 'active')
    readonly_fields = ('home', 'gid', 'uid')
    search_fields = ['username']
    ordering = ['username']

    def get_list_display(self, request):
        lst = super(AccountAdmin, self).get_list_display(request)
        tpe = type(lst)
        if request.user.has_perm('emailhosting.list_passwords'):
            return lst
        lst = list(lst)
        lst.remove('password')
        return tpe(lst)

    def get_form(self, request, obj=None, **kwargs):
        if obj and not request.user.has_perm('emailhosting.list_passwords'):
            return HiddenPasswordForm
        return super(AccountAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super(AccountAdmin, self).save_model(request, obj, form, change)
        if not change:
            self.message_user(
                request,
                _('User "%s" created with password "%s"') % (obj.username, obj.password),
                messages.WARNING
            )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'account', 'get_forward', 'standard')
    search_fields = ['local', 'account__username']
    ordering = ['local']
