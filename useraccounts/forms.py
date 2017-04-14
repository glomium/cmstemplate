#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from .conf import settings
from .models import Email
# from .validators import validate_password
# from .validators import help_text_password


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct login data. "
                           "Note that both fields may be case-sensitive."),
    }

    def __init__(self, request=None, field_placeholder=True, field_class='form-control', *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        model = get_user_model()

        if self.fields['username'].label is None:
            if settings.LOGIN_EMAIL and settings.LOGIN_USERNAME:
                self.fields['username'].label = _("Email or Username")
            elif settings.LOGIN_USERNAME:
                self.fields['username'].label = _("Username")
            elif settings.LOGIN_EMAIL:
                self.fields['username'].label = _("Email")
            else:
                self.fields['username'].label = capfirst(self.username_field.verbose_name)

        for fieldname in ['username', 'password']:
            field = self.fields.get(fieldname)
            if 'placeholder' not in field.widget.attrs and field_placeholder:
                field.widget.attrs['placeholder'] = field.label
            if field_class:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' ' + field_class
                else:
                    field.widget.attrs['class'] = field_class

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password, request=self.request)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication.
        This default behavior is to trust the authentification backend(s)
        """
        pass

    # compatability with django.contrib.admin
    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    # compatability with django.contrib.admin
    def get_user(self):
        return self.user_cache


class PasswordSetForm(forms.Form):
    """
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    field_names = ['new_password1', 'new_password2']

    new_password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

    def __init__(self, user, field_placeholder=True, field_class='form-control', *args, **kwargs):
        self.user = user
        super(PasswordSetForm, self).__init__(*args, **kwargs)
        self.help_text = help_text_password()

        for fieldname in self.field_names:
            field = self.fields.get(fieldname)
            if 'placeholder' not in field.widget.attrs and field_placeholder:
                field.widget.attrs['placeholder'] = field.label
            if field_class:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' ' + field_class
                else:
                    field.widget.attrs['class'] = field_class

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        # validation.password_changed(self.cleaned_data['new_password1'], self.user)
        return self.user

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        validate_password(password, self.user)
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2


class PasswordChangeForm(PasswordSetForm):
    """
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    }
    field_names = ['new_password1', 'new_password2', 'old_password']

    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput)

    def __init__(self, user, field_placeholder=True, field_class='form-control', *args, **kwargs):
        super(PasswordChangeForm, self).__init__(
            user,
            field_placeholder=field_placeholder,
            field_class=field_class,
            *args,
            **kwargs
        )
        self.help_text = help_text_password()

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        # validation.password_changed(self.cleaned_data['new_password1'], self.user)
        return self.user

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class PasswordRecoverForm(forms.Form):

    error_messages = {
        'email_notfound': _("This email address is invalid."),
    }

    email = forms.CharField(label=_("Email"))

    def __init__(self, request=None, field_placeholder=True, field_class='form-control', *args, **kwargs):
        self.request = request
        super(PasswordRecoverForm, self).__init__(*args, **kwargs)

        for fieldname in ['email']:
            field = self.fields.get(fieldname)
            if 'placeholder' not in field.widget.attrs and field_placeholder:
                field.widget.attrs['placeholder'] = field.label
            if field_class:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' ' + field_class
                else:
                    field.widget.attrs['class'] = field_class

    def clean_email(self):
        data = self.cleaned_data.get('email').lower()
        count = Email.objects.filter(email=data, is_valid=True).count()
        if count == 0:
            raise forms.ValidationError(
                self.error_messages['email_notfound'],
                code='email_notfound',
            )
        return data

    def save(self, commit=True):
        email = Email.objects.select_related('user').get(
            email=self.cleaned_data.get('email').lower(),
            is_valid=True,
        )
        email.send_restore(self.request)
        return email


class EmailCreateForm(forms.ModelForm):

    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())

    def __init__(self, user, request=None, field_placeholder=True, field_class='form-control', *args, **kwargs):
        self.request = request
        self.user = user
        super(EmailCreateForm, self).__init__(*args, **kwargs)

        for fieldname in ['email', 'password']:
            field = self.fields.get(fieldname)
            if 'placeholder' not in field.widget.attrs and field_placeholder:
                field.widget.attrs['placeholder'] = field.label
            if field_class:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' ' + field_class
                else:
                    field.widget.attrs['class'] = field_class

    def clean_email(self):
        return self.cleaned_data.get('email').lower()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError(_('Invalid password'))
        return password

    def save(self, commit=True):
        self.instance.user = self.user
        if commit:
            self.instance.save()
            self.instance.send_validation(self.request)
        return self.user

    class Meta:
        model = Email
        fields = [
            'email',
        ]
