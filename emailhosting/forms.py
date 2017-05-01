#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django import forms
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Account
from .models import validate_account_password


def password_validator(value):
    if 0 < len(value) < 7:
        raise ValidationError('Password is to small')


class HiddenPasswordForm(forms.ModelForm):
    pw1 = forms.CharField(
        label=_('New password'),
        widget=PasswordInput,
        required=False,
        validators=[validate_account_password])
    pw2 = forms.CharField(label=_('Confirm password'), widget=PasswordInput, required=False)

    def clean_pw2(self):
        if 'pw1' in self.cleaned_data and self.cleaned_data['pw1'] != self.cleaned_data['pw2']:
            raise ValidationError('Passwords don\'t match')

    def clean(self):
        data = super(HiddenPasswordForm, self).clean()
        if 'pw1' in data and data['pw1']:
            self.instance.password = data['pw1']
        return data
    
    class Meta:
        model = Account
        exclude = ['home', 'password']
