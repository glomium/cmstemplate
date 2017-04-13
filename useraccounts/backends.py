#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from datetime import timedelta


from .conf import settings
from .signals import login_success
from .signals import login_failed


import logging
logger = logging.getLogger(__name__)


class AuthBackend(ModelBackend):
    """
    Allow users to log in with their username or email address
    """

    error_messages = {
        'inactive': _("This account is inactive."),
        'denied': _("Login denied - please try again later"),
        'settings': _("The login is currently not available"),
    }

    def authenticate(self, **kwargs):
        """
        Checks it's kwargs and authenticates user

        also adds a throttle function, which limits the possible login attempts
        """
        # set variables
        model = get_user_model()
        email = model.emails.rel.related_model().__class__
        now = datetime.now()

        # get variables
        request = kwargs.pop('request', None)
        username = kwargs.pop('username', kwargs.pop('email', None))
        password = kwargs.pop('password', None)

        if settings.THROTTLE_IP:
            if not request:
                logger.critical(
                    'The authentification backend needs to be called with a request object or you need to deactivate THROTTLE_IP.'
                )
                raise ValidationError(
                    self.error_messages['settings'],
                    code='settings',
                )
            self.throttle_ip(request.META['REMOTE_ADDR'], now)

        # get user by username or email or password
        if username and password:

            # try to find the user by their email
            if settings.LOGIN_EMAIL:
                try:
                    validate_email(username)
                    obj = email.objects.filter(
                        is_valid=True,
                    ).select_related('user').order_by('is_primary').get(email=username.lower())
                except ValidationError:
                    pass
                except email.DoesNotExist:
                    pass
                else:
                    if settings.THROTTLE_USER:
                        self.throttle_user(obj.user.pk, now)

                    if obj.user.check_password(password):
                        if self.user_can_authenticate(obj.user):
                            self.login_success(username, "email", obj.user)
                            return obj.user
                        else:
                            raise ValidationError(
                                self.error_messages['inactive'],
                                code='inactive',
                            )
                        return None
                    self.login_failed(request, username, "email", now, obj.user)
                    return None

            # try to find the user by their username
            if settings.LOGIN_USERNAME:
                try:
                    user = model._default_manager.get_by_natural_key(username)
                except model.DoesNotExist:
                    # Run the default password hasher once to reduce the timing
                    # difference between an existing and a non-existing user (#20760).
                    model().set_password(password)
                else:
                    if settings.THROTTLE_USER:
                        self.throttle_user(user.pk, now)

                    if user.check_password(password):
                        if self.user_can_authenticate(user):
                            self.login_success(username, "username", user)
                            return user
                        else:
                            raise ValidationError(
                                self.error_messages['inactive'],
                                code='inactive',
                            )
                        return None
                    self.login_failed(request, username, "username", now, user)
                    return None

            self.login_failed(request, username, "nomatch", now)

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def login_success(self, name, via, user):
        """
        this function is called if a user got logged in
        """
        login_success.send(sender=self.__class__, user=user)
        logger.info('Sucessful login for "%s" (#%s) via %s', name, user.pk, via)

    def login_throttled(self, via, name):
        """
        this function is called if a login was rejected due to throtteling
        """
        logger.warning('Login denied for "%s" via %s', name, via)
        raise ValidationError(
            self.error_messages['denied'],
            code='denied',
        )

    def login_failed(self, request, name, via, now, user=None):
        """
        this function is called if a login failed
        """
        if settings.THROTTLE_IP:
            if request.META['REMOTE_ADDR'] not in settings.INTERNAL_IPS:
                try:
                    cache.incr(self.key('ip', request.META['REMOTE_ADDR'], now), 1)
                except ValueError:
                    cache.set(self.key('ip', request.META['REMOTE_ADDR'], now), 1, (settings.THROTTLE_IP_INTERVAL + 1) * 60)

        if user:
            logger.warning('Login failed for "%s" (#%s) via %s', name, user.pk, via)
            if settings.THROTTLE_USER:
                try:
                    cache.incr(self.key('user', user.pk, now), 1)
                except ValueError:
                    cache.set(self.key('user', user.pk, now), 1, (settings.THROTTLE_USER_INTERVAL + 1) * 60)

            # emit a signal if the login failed
            cache_key = '%s-%s-%s' % (
                settings.CACHE_PREFIX,
                'loginfail',
                user.pk,
            )
            if not settings.THROTTLE_SIGNAL_TIMEOUT or cache.get(cache_key):
                login_failed.send(sender=self.__class__, user=user, seen=bool(settings.THROTTLE_SIGNAL_TIMEOUT))
            else:
                cache.set(cache_key, 1, settings.THROTTLE_SIGNAL_TIMEOUT * 60)
                login_failed.send(sender=self.__class__, user=user, seen=False)

        else:
            logger.warning('Login failed for "%s" via %s', name, via)

    def key(self, via, value, time):
        return '%s-%s-%s-%s' % (
            settings.CACHE_PREFIX,
            via,
            value,
            time.strftime('%Y%m%d%H%M'),
        )

    def get_keys(self, via, value, now, interval):
        for minute in range(interval + 1):
            yield self.key(via, value, now - timedelta(minutes=minute))

    def throttle_user(self, pk, now):
        counts = cache.get_many(list(
            self.get_keys(
                "user",
                pk,
                now,
                settings.THROTTLE_USER_INTERVAL,
            )
        ))
        if sum(counts.values()) >= settings.THROTTLE_USER_COUNT:
            self.login_throttled("user", pk)

    def throttle_ip(self, address, now):
        counts = cache.get_many(list(
            self.get_keys(
                "ip",
                address,
                now,
                settings.THROTTLE_IP_INTERVAL,
            )
        ))
        if sum(counts.values()) >= settings.THROTTLE_IP_COUNT:
            self.login_throttled("ip", address)
