#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib import admin
# from django.utils.translation import ugettext_lazy as _

from .models import ACL


@admin.register(ACL)
class ACLAdmin(admin.ModelAdmin):
    pass
