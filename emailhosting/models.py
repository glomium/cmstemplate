#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model
from django.db import connections
from django.db import models
from django.db.utils import IntegrityError
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
# from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from useraccounts.signals import email_changed
from useraccounts.signals import user_activated
from useraccounts.signals import user_deactivated
from useraccounts.signals import user_validated

import logging
import re

from random import choice
# from socket import getfqdn
# from socket import gethostbyname
# from Crypto.PublicKey import RSA


logger = logging.getLogger(__name__)


GNAME_DEFAULT = "default"


# === VALIDATIONS =============================================================


def validate_account_username(value):
    if not re.match(r'^([a-z0-9-._]+)$', value):
        raise ValidationError(_("You can only use small case chars, numbers, the dot and dashes"))
    return True


def validate_account_groupname(value):
    if not re.match(r'^([a-z0-9-._]+)$', value):
        raise ValidationError(_("You can only use small case chars, numbers, the dot and dashes"))
    return True


def validate_account_password(value):
    try:
        value.encode('ascii')
    except UnicodeEncodeError:
        raise ValidationError(_("The password contains non-ascii characters"))
    if 0 < len(value) < 7:
        raise ValidationError('Password is to small, use more than 8 chars')
    if '\\' in value:
        raise ValidationError('The char \\ is forbidden')
    return True


def validate_address_local(value):
    if value and not re.match(r'^([a-z0-9-._]+)$', value):
        raise ValidationError(_("You can only use small case chars, numbers, the dot and dashes"))
    return True


def validate_address_forward(value):
    validator = EmailValidator()
    if value:
        for mail in value.splitlines():
            validator(mail)
    return True


# === MODELS ==================================================================


@python_2_unicode_compatible
class Domain(models.Model):
    """
    """
    subdomain = models.CharField(_("Subdomain"), max_length=100, null=True, blank=True)
    name = models.CharField(_("Domainname"), max_length=100, null=True, blank=False)
    tld = models.CharField(_("Top-Level-Domain"), max_length=10, null=True, blank=False)

    full_name = models.CharField(_("Domainname"), max_length=255, null=True, editable=False)
#   mailhost = models.ForeignKey(MailServer, null=True, blank=False, related_name="+")
    accept_mail = models.BooleanField(_("Accept Emails"), default=True)
#   dkim_public = models.TextField(_("DKIM (private-key)"), null=False, blank=True)
#   dkim_selector = models.CharField(_("DKIM (selector)"), max_length=16, null=True, blank=False, default=DKIM_SELECTOR)
#   domainkey = models.TextField(_("DomainKey"), null=False, blank=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.subdomain:
            self.full_name = '%s.%s.%s' % (self.subdomain, self.name, self.tld)
        else:
            self.full_name = '%s.%s' % (self.name, self.tld)

#       if not self.dkim_public:
#           if self.subdomain:
#               try:
#                   self.dkim_public = Domain.objects.get(name=self.name, tld=self.tld, subdomain="").domainkey
#               except Domain.DoesNotExist:
#                   self.dkim_public = RSA.generate(1024).exportKey()
#           else:
#               self.dkim_public = RSA.generate(1024).exportKey()

        super(Domain, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')
        unique_together = (('subdomain', 'name', 'tld'),)

#   def public_domainkey(self):
#       try:
#           private = RSA.importKey(text)
#       except ValueError:
#           return _("Error in private Key")
#       return ''.join(private.publickey().exportKey().split('\n')[1:-1])


@python_2_unicode_compatible
class Account(models.Model):
    """
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    username = models.CharField(_("Username"), max_length=64, null=True, blank=False, db_index=True, unique=True, validators=[validate_account_username])
    password = models.CharField(_("Password"), max_length=64, null=True, blank=True, db_index=True, validators=[validate_account_password])

    quota = models.PositiveIntegerField(
        _("Quota in MB"),
        default=0,
        help_text=_('A value of 0 means unlimited'),
    )

    uid = models.CharField(
        _("User ID"),
        max_length=32,
        null=True,
        blank=False,
        default="vmail",
        help_text=_('Sets the user under wich the delivery process runs'),
    )
    gid = models.CharField(
        _("Group ID"),
        max_length=32,
        null=True,
        blank=False,
        default="vmail",
        help_text=_('Sets the group under wich the delivery process runs'),
    )
    gname = models.CharField(
        _("Groupname"),
        max_length=32,
        null=True,
        blank=False,
        default=GNAME_DEFAULT,
        validators=[validate_account_groupname],
        editable=False,
        help_text=_('Used to fragment the default user directoryies'),
    )
    home = models.CharField(
        _("Directory"),
        max_length=200,
        null=True,
        blank=True,
        help_text=_('Imap-directory for the user. Renaming does not move the old directory!'),
    )

    active = models.BooleanField(_("Is active"), default=True, db_index=True)

    def __str__(self):
        return '%s' % (self.username)

    def clean(self):
        if not self.password:
            self.gen_password()
        if not self.home and self.gname and self.username:
            self.home = '/opt/vmail/' + self.gname + '/' + self.username

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
        permissions = (
            ('list_passwords', 'Lists passwords in AdminView'),
        )

    def gen_password(self, length=12):
        password = ''
        string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890123456789-_=+!?-_=+!?'
        for i in range(length):
            password += choice(string)
        self.password = password
        return password


def post_save_account(sender, instance, created, **kwargs):
    cursor = connections['default'].cursor()
    cursor.execute(
        "UPDATE roundcube_users SET username=%s, mail_host=%s WHERE user_id=%s;",
        [
            '%s' % instance.username,
            'localhost',
            instance.pk,
        ]
    )
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO roundcube_users (user_id, username, mail_host) VALUES (%s, %s, %s);",
            [
                instance.pk,
                '%s' % instance.username,
                'localhost',
            ]
        )


post_save.connect(post_save_account, sender=Account, dispatch_uid="account_post_save")


def post_delete_account(sender, instance, **kwargs):
    cursor = connections['default'].cursor()
    cursor.execute(
        "DELETE FROM roundcube_users WHERE user_id=%s;",
        [
            instance.pk,
        ]
    )


post_delete.connect(post_delete_account, sender=Account, dispatch_uid="account_post_delete")


@python_2_unicode_compatible
class List(models.Model):
    """
    """
    name = models.CharField(max_length=100, null=False, blank=False)

    to_members = models.BooleanField(
        default=False,
        help_text="Send mail to all members",
    )

    check_sender = models.PositiveSmallIntegerField(
        choices=(
            (0, "Allow all senders"),
            (1, "Allow all subscribers"),
            (2, "Allow all members"),
            (3, "Allow only priviledged subscribers"),
        ),
        default=3,
        blank=True,
        null=False,
        help_text="Check sender email address"
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Is the list subscribable from non registered users",
    )

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self._to_members = self.to_members
        self._is_public = self.is_public
        self._check_sender = self.check_sender

    def save(self, *args, **kwargs):
        ret = super(List, self).save(*args, **kwargs)

        if self._to_members != self.to_members and self.to_members:

            # select all active and valid members and add them to the list
            for user in get_user_model().objects.filter(is_active=True, is_valid=True):
                try:
                    self.subscriber_set.filter(email=user.email, user=None).update(user=user)
                    self.subscriber_set.create(
                        user=user,
                        email=user.email,
                        can_send=(self.check_sender < 3),
                    )
                except IntegrityError:
                    pass

        if self._check_sender < self.check_sender and self.check_sender in [1, 2]:
            self.update_senders()

        if self._is_public != self.is_public and not self.is_public:
            self.subscriber_set.filter(user__isnull=True).delete()

        return ret

    def update_senders(self):
        if self.check_sender == 1:
            # update all subscribers
            self.subscriber_set.all().update(can_send=True)
        if self.check_sender == 2:
            # update all subscribed members
            self.subscriber_set.filter(user__isnull=False).update(can_send=True)


@python_2_unicode_compatible
class Subscriber(models.Model):
    """
    """
    mailinglist = models.ForeignKey(List, blank=False, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    can_send = models.BooleanField(default=False, help_text="is allowed to send messages")

    class Meta:
        unique_together = [
            ('mailinglist', 'email'),
        ]

    def clean(self):

        if self.user and self.user.is_valid and self.user.email:
            self.email = self.user

        if not self.email and not self.user:
            raise ValidationError(_("You need an user or email adress"))

        if self.mailinglist.check_sender < 3 and self.user or self.mailinglist.check_sender < 2 and not self.user:
            self.can_send = True

    def __str__(self):
        if self.user:
            return '%s #%s' % (self.email, self.user_id)
        else:
            return self.email


@python_2_unicode_compatible
class Address(models.Model):
    """
    """
    local = models.CharField(
        _("Local"),
        max_length=100,
        null=True, blank=True,
        help_text=_("Use blank to catch all"),
        validators=[validate_address_local],
    )
    domain = models.ForeignKey(Domain, null=True, blank=False, related_name="mail_address")
    account = models.ForeignKey(Account, null=True, blank=True, related_name="mail_address")
    mailinglist = models.ForeignKey(List, null=True, blank=True, related_name="mail_address")
    forward = models.TextField(_("Forward"), null=True, blank=True, validators=[validate_address_forward])
    catchall = models.BooleanField(default=False, editable=False)
    standard = models.BooleanField(default=False)

    def clean(self):
        if not self.local:
            self.local = None
        if not self.get_forward:
            self.forward = None
        if not self.account_id:
            self.account_id = None
        if not self.mailinglist_id:
            self.mailinglist_id = None
        if self.forward and not self.local:
            raise ValidationError(_("You can not set a forward with catchall"))
        if self.mailinglist and not self.local:
            raise ValidationError(_("You can not create a catchall mailinglist"))
        if not self.account_id and not self.forward and not self.mailinglist:
            raise ValidationError(_("You must either define an account or mailinglist or a forward target or both"))

    def __str__(self):
        if self.local:
            return self.get_mail()
        else:
            return 'catchall (%s)' % self.domain.full_name

    def get_mail(self):
        return '%s@%s' % (self.local, self.domain.full_name)
    get_mail.short_description = _('Email')

    def get_forward(self):
        if not self.forward:
            return ''
        return mark_safe('<br>'.join(self.forward.splitlines()))
    get_forward.short_description = _('Forward')

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Address')
        unique_together = (('local', 'domain'), )


def pre_save_address(sender, instance, **kwargs):
    instance.catchall = False
    if not instance.local and not instance.forward:
        instance.catchall = True
        instance.standard = False
        instance.local = None


pre_save.connect(pre_save_address, sender=Address, dispatch_uid="address_pre_save")


def post_save_address(sender, instance, created, **kwargs):
    if not instance.pk and instance.local:
        if Address.objects.filter(account_id=instance.account_id).count() == 0:
            instance.standard = True
    elif instance.standard and instance.local:
        Address.objects.filter(account_id=instance.account_id).exclude(pk=instance.pk).update(standard=False)

    cursor = connections['default'].cursor()
    if instance.local and instance.account_id:
        cursor.execute(
            "UPDATE roundcube_identities SET user_id=%s, email=%s, standard=%s WHERE identity_id=%s;",
            [
                '%s' % instance.account_id,
                '%s' % instance.get_mail(),
                '%s' % 1 if instance.standard else 0,
                instance.pk,
            ]
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO roundcube_identities (identity_id, user_id, name, email, standard) VALUES (%s, %s, %s, %s, 1);",
                [
                    instance.pk,
                    '%s' % instance.account_id,
                    '%s' % instance.get_mail(),
                    '%s' % instance.get_mail(),
                ]
            )
        if instance.standard:
            "UPDATE roundcube_identities SET standard=0 WHERE user_id=%s AND NOT identity_id=%s;",
            [
                '%s' % instance.account_id,
                instance.pk,
            ]
    else:
        cursor.execute(
            "DELETE FROM roundcube_identities WHERE identity_id=%s;",
            [
                instance.pk,
            ]
        )


post_save.connect(post_save_address, sender=Address, dispatch_uid="address_post_save")


def post_delete_address(sender, instance, **kwargs):
    cursor = connections['default'].cursor()
    cursor.execute(
        "DELETE FROM roundcube_identities WHERE identity_id=%s;",
        [
            instance.pk,
        ]
    )


post_delete.connect(post_delete_address, sender=Address, dispatch_uid="address_post_delete")


# === SIGNAL LOGIC ============================================================


def user_activated_list(sender, user, **kwargs):
    logger.debug("ACTIVATE USER ON MAILINGLISTS")

    # udate email adresses without user instance
    Subscriber.objects.filter(email=user.email, user__isnull=True).update(user=user)

    # add user automatically to mailinglists
    for mailinglist in List.objects.filter(to_members=True):
        mailinglist.subscriber_set.create(
            user=user,
            email=user.email,
            can_send=mailinglist.check_sender < 3
        )

    # update permissions
    Subscriber.objects.filter(
        user=user,
        can_send=False,
        mailinglist__check_sender__lt=3
    ).update(can_send=True)


def user_deactivated_list(sender, user, **kwargs):
    logger.debug("DEACTIVATE USER FROM MAILINGLIST")

    # remove user from all lists with is_public=False
    Subscriber.objects.filter(user=user, mailinglist__is_public=False).delete()

    # remove permissions with lists which allow all members to publish
    Subscriber.objects.filter(
        user=user,
        can_send=True,
        mailinglist__check_sender=2
    ).update(can_send=False)


def email_changed_list(sender, user, email, **kwargs):
    logger.debug("CHANGE USER MAIL ON MAILINGLISTS")

    # update email adresses without user instance
    Subscriber.objects.filter(email=email, user__isnull=True).update(user=user)

    # update email address for all subscriptions of this account
    for acc in Subscriber.objects.filter(user=user):
        acc.email = email

        try:
            acc.save()

        except IntegrityError:

            perm = max(Subscriber.objects.filter(
                user=user,
                mailinglist=acc.mailinglist
            ).values_list("can_send", flat=True))

            # delete lists where the user is twice
            Subscriber.objects.filter(
                user=user,
                mailinglist=acc.mailinglist
            ).exclude(
                id=acc.id
            ).delete()

            acc.can_send = perm
            acc.save()


# === CONNECT SIGNALS =========================================================


user_activated.connect(user_activated_list, dispatch_uid="list_user_activated")
user_validated.connect(user_activated_list, dispatch_uid="list_user_validated")
user_deactivated.connect(user_deactivated_list, dispatch_uid="list_user_deactivated")
email_changed.connect(email_changed_list, dispatch_uid="list_email_changed")
