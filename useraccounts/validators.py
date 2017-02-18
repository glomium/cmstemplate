#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import lru_cache
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

import re

from .conf import settings as appsettings


@lru_cache.lru_cache(maxsize=None)
def get_default_username_validators():
    return get_validators(appsettings.USERNAME_VALIDATORS)


@lru_cache.lru_cache(maxsize=None)
def get_default_password_validators():
    return get_validators(getattr(settings, 'AUTH_PASSWORD_VALIDATORS', []))


def get_validators(config):
    validators = []
    for validator in config:
        try:
            klass = import_string(validator['NAME'])
        except ImportError:
            msg = "The module in NAME could not be imported: %s. Check your settings."
            raise ImproperlyConfigured(msg % validator['NAME'])
        validators.append(klass(**validator.get('OPTIONS', {})))

    return validators


def validate_password(password, user=None):
    """
    Validate whether the password meets all validator requirements.

    If the password is valid, return ``None``.
    If the password is invalid, raise ValidationError with all error messages.
    """
    errors = []
    password_validators = get_default_password_validators()
    for validator in password_validators:
        try:
            validator.validate(password, user)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)


def validate_username(username):
    errors = []
    validators = get_default_username_validators()
    for validator in validators:
        try:
            validator.validate(username)
        except ValidationError as error:
            errors.append(error)
    if errors:
        raise ValidationError(errors)


def help_text_password():
    text = []
    validators = get_default_password_validators()
    for validator in validators:
        text.append(validator.get_help_text())
    return text


class MinimumLengthValidator(object):
    """
    Validate whether the password is of a minimum length.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password is too short. It must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("The password must contain at least %(min_length)d characters.") % {'min_length': self.min_length}


class BaseCountValidator(object):
    """
    Validate whether the password is of a minimum length.
    """
    verbose_name = None
    verbose_name_plural = None

    def __init__(self, min_length=1):
        self.min_length = min_length

    def count(self, password):
        raise NotImplementedError

    def validate(self, password, user=None):
        if self.count(password) < self.min_length:
            if self.min_length > 1:
                raise ValidationError(
                    _("The password must contain at least %(min_length)d %(name)s."),
                    code='number_count_too_short',
                    params={
                        'min_length': self.min_length,
                        'name': self.verbose_name_plural,
                    },
                )
            else:
                raise ValidationError(
                    _("The password must contain at least %(name)s."),
                    code='number_count_too_short',
                    params={
                        'name': self.verbose_name,
                    },
                )

    def get_help_text(self):
        if self.min_length > 1:
            return _("The password must contain at least %(name)s.") % self.verbose_name
        else:
            return _("The password must contain at least %(min_length)d %(name)s.") % {
                'min_length': self.min_length,
                'name': self.verbose_name_plural
            }

class RegexValidator(object):
    expression = r'.*'
    inverse_match = False
    code = "invalid"
    flags = None
    message = _("Expression must match %(expression)s")
    help_text = _("Expression must match %(expression)s")


    def validate(self, value, user=None):
        if not hasattr(self, 'regex'):
            if self.flags:
                self.regex = re.compile(self.expression, self.flags)
            else:
                self.regex = re.compile(self.expression)
        if not (self.inverse_match is not bool(self.regex.search(force_text(value)))):
            raise ValidationError(self.message % {'expression': self.expression}, code=self.code)

    def get_help_text(self):
        return self.help_text % {'expression': self.expression}


class NumericCharCountValidator(BaseCountValidator):
    verbose_name = _("one number")
    verbose_name_plural = _("numbers")

    def count(self, password):
        count = 0
        for char in password:
            if char.isdigit():
                count += 1
        return count


class LowerCharCountValidator(BaseCountValidator):
    verbose_name = _("one lower character")
    verbose_name_plural = _("lower characters")

    def count(self, password):
        count = 0
        for char in password:
            if char.islower():
                count += 1
        return count


class UpperCharCountValidator(BaseCountValidator):
    verbose_name = _("one upper character")
    verbose_name_plural = _("upper characters")

    def count(self, password):
        count = 0
        for char in password:
            if char.isupper():
                count += 1
        return count


class SpecialCharCountValidator(BaseCountValidator):
    verbose_name = _("one special character")
    verbose_name_plural = _("special characters")

    def count(self, password):
        count = 0
        for char in password:
            if not char.isupper() and not char.islower() and not char.isdigit():
                count += 1
        return count


class UsernameValidator(RegexValidator):
    expression = r'^[\w.@+-]+$'
    message = _("Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.")
    help_text =  _("The username may contain only letters, numbers and @/./+/-/_ characters.")
