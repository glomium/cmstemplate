#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
# from django.contrib.auth.models import PermissionsMixin
from django.core.mail.message import EmailMultiAlternatives
from django.core.signing import BadSignature
from django.core.signing import SignatureExpired
from django.core.signing import TimestampSigner
# from django.core.urlresolvers import reverse
# from django.core.urlresolvers import NoReverseMatch
from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .conf import settings as appsettings
from .signals import email_changed
from .signals import email_validated
from .signals import user_activated
from .signals import user_deactivated
from .signals import user_validated
from .signals import validation_send
from .signals import password_restore_send


import logging
logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """
    BaseUserManager from django.contrib

    updateing create_user and create_superuser so that they don't require
    a email-address for the creation
    """

    def _create_user(self, username, password):
        if not username:
            raise ValueError('The given username must be set')

        username = self.model.normalize_username(username)
        user = self.model(username=username)
        user.set_password(password)

        return user

    def create_user(self, username, password=None):
        user = self._create_user(username, password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self._create_user(username, password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


@python_2_unicode_compatible
class User(AbstractUser):
    is_valid = models.BooleanField(_('Has valid email'), default=False,
        help_text=_('Indicates if the user has a valid email address.')
    )
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def add_email(self, emailaddress, request=None, skip=False):
        email = self.emails.create(email=emailaddress)
        stamp, crypt = email.send_validation(request, skip)
        return {"email": email, "stamp": stamp, "crypt": crypt}

    def make_email_invalid(self):
        """
        Marks the current email-address as invalid
        """
        self.is_valid = False
        self.emails.filter(is_primary=True).update(is_primary=False, is_valid=False, validated=None)
        self.save()

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if self.pk:
            self._original_active = self.is_active
        else:
            self._original_active = False

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        if not self._original_active and self.is_active:
            user_activated.send(sender=self.__class__, user=self)
        if self._original_active and not self.is_active:
            user_deactivated.send(sender=self.__class__, user=self)


@python_2_unicode_compatible
class Email(models.Model):
    email = models.EmailField(_('Email Address'), blank=False, db_index=True, null=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emails",
        null=False,
        blank=False,
    )

    is_primary = models.BooleanField(
        _('primary'),
        default=False,
        db_index=True,
    )
    is_valid = models.BooleanField(
        _('valid'),
        default=False,
        db_index=True,
    )
    validated = models.DateTimeField(_('validated'), editable=False, null=True, blank=True)

    created = models.DateTimeField(_('created'), editable=False, auto_now_add=True)
    updated = models.DateTimeField(_('updated'), editable=False, auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)
        self.original_primary = self.is_primary

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        data = super(Email, self).save(*args, **kwargs)
        self.update_primary()
        return data

    def get_validation_signer(self):
        return TimestampSigner(salt=appsettings.VALIDATION_SALT)

    def get_restore_signer(self):
        return TimestampSigner(salt=appsettings.RESTORE_SALT)

    def get_activation_credentials(self):
        return self.get_validation_signer().sign(self.email).split(':')[1:3]

    def get_restore_credentials(self):
        return self.get_restore_signer().sign(self.user.password).split(':')[1:3]

    def send_validation(self, request=None, skip=False):
        stamp, crypt = self.get_activation_credentials()

        if not skip and appsettings.VALIDATION_SEND_MAIL:
            html = None
            if appsettings.VALIDATION_TEMPLATE_HTML:
                try:
                    html = get_template(appsettings.VALIDATION_TEMPLATE_HTML)
                except TemplateDoesNotExist:
                    pass

            plain = None
            if appsettings.VALIDATION_TEMPLATE_PLAIN:
                try:
                    plain = get_template(appsettings.VALIDATION_TEMPLATE_PLAIN)
                except TemplateDoesNotExist:
                    pass

            try:
                subject = get_template(appsettings.VALIDATION_TEMPLATE_SUBJECT)
            except TemplateDoesNotExist:
                subject = None

            if subject and (html or plain):
                context = {
                    'user': self.user,
                    'email': self.email,
                    'stamp': stamp,
                    'crypt': crypt,
                    'viewname': appsettings.RESOLVE_EMAIL_VALIDATE,
                    'timeout': appsettings.VALIDATION_TIMEOUT,
                    'request': request,
                }

                message = EmailMultiAlternatives(subject.render(context).strip(), to=[self.email])

                if plain and html:
                    message.body = plain.render(context).strip()
                    message.attach_alternative(html.render(context).strip(), "text/html")
                elif html:
                    message.body = html.render(context).strip()
                    message.content_subtype = "html"
                else:
                    message.body = plain.render(context).strip()
                message.send()
            else:
                logger.critical("No subject or text provided for validation email. Sending validation-mail to %s aborted", self.email)

        validation_send.send(sender=self.__class__, user=self.user, email=self.email, stamp=stamp, crypt=crypt, skip=skip)
        logger.info("%s has requested an email-validation for %s", self.user, self.email)
        return (stamp, crypt)

    def send_restore(self, request=None, skip=False):
        stamp, crypt = self.get_restore_credentials()

        if not skip and appsettings.RESTORE_SEND_MAIL:
            html = None
            if appsettings.RESTORE_TEMPLATE_HTML:
                try:
                    html = get_template(appsettings.RESTORE_TEMPLATE_HTML)
                except TemplateDoesNotExist:
                    pass

            plain = None
            if appsettings.RESTORE_TEMPLATE_PLAIN:
                try:
                    plain = get_template(appsettings.RESTORE_TEMPLATE_PLAIN)
                except TemplateDoesNotExist:
                    pass

            try:
                subject = get_template(appsettings.RESTORE_TEMPLATE_SUBJECT)
            except TemplateDoesNotExist:
                subject = None

            if subject and (html or plain):
                context = {
                    'user': self.user,
                    'email': self.email,
                    'stamp': stamp,
                    'crypt': crypt,
                    'viewname': appsettings.RESOLVE_PASSWORD_RESTORE,
                    'timeout': appsettings.RESTORE_TIMEOUT,
                    'request': request,
                }

                message = EmailMultiAlternatives(subject.render(context).strip(), to=[self.email])

                if plain and html:
                    message.body = plain.render(context).strip()
                    message.attach_alternative(html.render(context).strip(), "text/html")
                elif html:
                    message.body = html.render(context).strip()
                    message.content_subtype = "html"
                else:
                    message.body = plain.render(context).strip()
                message.send()
            else:
                logger.critical(
                    "No subject or text provided for password restore. Sending validation-mail to %s aborted",
                    self.email,
                )

        password_restore_send.send(sender=self.__class__, user=self.user, email=self.email, stamp=stamp, crypt=crypt, skip=skip)
        logger.info("%s has requested a password restore for %s", self.user, self.email)
        return (stamp, crypt)

    def check_validation(self, stamp, crypt):
        value = '%s:%s:%s' % (self.email, stamp, crypt)
        try:
            return self.get_validation_signer().unsign(value, max_age=(appsettings.VALIDATION_TIMEOUT * 3600))
        except BadSignature:
            return None
        except SignatureExpired:
            return None

    def check_restore(self, stamp, crypt):
        value = '%s:%s:%s' % (self.user.password, stamp, crypt)
        try:
            return self.get_restore_signer().unsign(value, max_age=(appsettings.RESTORE_TIMEOUT * 3600))
        except BadSignature:
            return None
        except SignatureExpired:
            return None

    def update_primary(self):

        # update the users email address, if they don't match
        # this can happen if the users email-addres is not set
        # on the user creation
        if self.is_primary and self.user.email != self.email:
            self.user.email = self.email
            if self.is_valid:
                if not self.user.is_valid:
                    user_validated.send(sender=self.__class__, user=self.user)
                self.user.is_valid = True
            self.user.save()

        if self.is_primary and not self.original_primary:
            self.__class__.objects.filter(user=self.user).exclude(pk=self.pk).update(is_primary=False)
            email_changed.send(sender=self.__class__, user=self.user, email=self.email)
            logger.info("%s has changed primary email to %s", self.user, self.email)

    def validate(self):
        self.is_valid = True

        if not self.user.is_valid:
            self.user.is_valid = True
            self.is_primary = True
            self.update_primary()
            user_validated.send(sender=self.__class__, user=self.user)
            self.user.save()
            logger.info("%s is now valid", self.user)

        self.validated = timezone.now()
        self.save()

        email_validated.send(sender=self.__class__, user=self.user, email=self.email)
        logger.info("%s has validated %s", self.user, self.email)

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')
        ordering = ["email"]
