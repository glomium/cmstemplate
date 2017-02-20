#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _



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
                    _("The password must contain at least one %(name)s."),
                    code='number_count_too_short',
                    params={
                        'name': self.verbose_name,
                    },
                )

    def get_help_text(self):
        if self.min_length > 1:
            return _("The password must contain at least one %(name)s.") % self.verbose_name
        else:
            return _("The password must contain at least %(min_length)d %(name)s.") % {
                'min_length': self.min_length,
                'name': self.verbose_name_plural
            }


class NumericCharCountValidator(BaseCountValidator):
    verbose_name = _("number")
    verbose_name_plural = _("numbers")

    def count(self, password):
        count = 0
        for char in password:
            if char.isdigit():
                count += 1
        return count


class LowerCharCountValidator(BaseCountValidator):
    verbose_name = _("lower character")
    verbose_name_plural = _("lower characters")

    def count(self, password):
        count = 0
        for char in password:
            if char.islower():
                count += 1
        return count


class UpperCharCountValidator(BaseCountValidator):
    verbose_name = _("upper character")
    verbose_name_plural = _("upper characters")

    def count(self, password):
        count = 0
        for char in password:
            if char.isupper():
                count += 1
        return count


class SpecialCharCountValidator(BaseCountValidator):
    verbose_name = _("special character")
    verbose_name_plural = _("special characters")

    def count(self, password):
        count = 0
        for char in password:
            if not char.isupper() and not char.islower() and not char.isdigit():
                count += 1
        return count
