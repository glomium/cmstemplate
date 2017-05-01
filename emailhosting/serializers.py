#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.utils.formats import date_format

from djangobmf.serializers import ModuleSerializer

from rest_framework import serializers

from .models import Domain
from .models import MailAccount
from .models import MailAddress


class DomainSerializer(ModuleSerializer):
    class Meta:
        model = Domain
        fields = (
            'subdomain',
            'name',
            'tld',
            'accept_mail',
            'full_name',
            'bmfdetail',
        )


class MailAccountSerializer(ModuleSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    customer_name = serializers.ReadOnlyField(source='customer.name')

    class Meta:
        model = MailAccount
        fields = (
            'customer',
            'customer_name',
            'project',
            'project_name',
            'username',
            'quota',
            'active',
            'bmfdetail',
        )


class MailAddressSerializer(ModuleSerializer):
    domain_name = serializers.ReadOnlyField(source='domain.full_name')
    account_name = serializers.ReadOnlyField(source='account.username')
    account_url = serializers.SerializerMethodField()

    class Meta:
        model = MailAddress
        fields = (
            'local',
            'domain',
            'domain_name',
            'account',
            'account_name',
            'account_url',
            'standard',
            'bmfdetail',
        )

    def get_account_url(self, obj):
        return obj.account.bmfmodule_detail()
