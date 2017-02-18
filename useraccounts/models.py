#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail.message import EmailMultiAlternatives
from django.core.signing import BadSignature
from django.core.signing import SignatureExpired
from django.core.signing import TimestampSigner
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.db import models
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .conf import settings as appsettings
from .signals import email_changed
from .signals import email_validated
from .signals import user_validated
from .signals import validation_send
from .signals import password_restore_send
from .validators import validate_username
# from .validators import validate_password


import logging
logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.model(username=username)
        user.is_staff = True
        user.is_valid = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        db_index=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[validate_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True, editable=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    is_valid = models.BooleanField(_('valid'), default=False,
        help_text=_('Designates if the user has a valid email address.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        abstract = True

    def add_email(self, emailaddress, request=None, skip=False):
        email = self.emails.create(email=emailaddress)
        stamp, crypt = email.send_validation(request, skip)
        return {"email": email, "stamp": stamp, "crypt": crypt}

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


@python_2_unicode_compatible
class AbstractEmail(models.Model):
    email = models.EmailField(_('email address'), blank=False, db_index=True, null=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="emails", null=False, blank=False)

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
        super(AbstractEmail, self).__init__(*args, **kwargs)
        self.original_primary = self.is_primary

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        data = super(AbstractEmail, self).save(*args, **kwargs)
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
                logger.critical("No subject or text provided for password restore. Sending validation-mail to %s aborted", self.email)

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
        abstract = True
        ordering = ["email"]


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        abstract = False


class Email(AbstractEmail):
    class Meta(AbstractEmail.Meta):
        abstract = False
