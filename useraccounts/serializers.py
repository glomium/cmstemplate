#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.signing import BadSignature
from django.core.signing import SignatureExpired

from rest_framework import fields
from rest_framework import serializers

from .models import Email
from .models import User
from .validators import validate_password
from .validators import validate_username


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', 'last_name')
        read_only_fields = ('is_staff', 'email', 'is_active')
        extra_kwargs = {
            'url': {'lookup_field': 'username'},
        }


class EmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('url', 'email', 'is_primary', 'is_valid')
        read_only_fields = ('is_primary', 'is_valid')
        extra_kwargs = {
            'url': {'lookup_field': 'email'},
        }


class EmailDetailSerializer(EmailListSerializer):
    class Meta(EmailListSerializer.Meta):
        read_only_fields = ('email', 'is_valid')


class EmailValidate(serializers.Serializer):
    stamp = fields.CharField(allow_blank=False, trim_whitespace=True)
    crypt = fields.CharField(allow_blank=False, trim_whitespace=True)

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        try:
            self.instance.check_validation(data['stamp'], data['crypt'])
        except BadSignature:
            raise serializers.ValidationError("Validation code invalid.")
        except SignatureExpired:
            raise serializers.ValidationError("Validation code expired.")
        return data

    def update(self, instance, validated_data):
        instance.validate()
        return instance


class UsernameValidate(serializers.Serializer):
    username = fields.CharField(allow_blank=False, trim_whitespace=True)
    def validate(self, data):
        """
        """
        validate_username(data["username"])
        return data


class PasswordValidate(serializers.Serializer):
    password = fields.CharField(allow_blank=False, trim_whitespace=True)
    def validate(self, data):
        """
        """
        validate_password(data["password"], self.instance)
        return data
