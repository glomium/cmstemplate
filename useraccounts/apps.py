#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'useraccounts'
    label = 'useraccounts'
    verbose_name = "Accounts"
