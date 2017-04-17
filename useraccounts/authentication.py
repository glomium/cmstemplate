#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _


from rest_framework.authentication import get_authorization_header
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt

from .utils import decode_handler


class JWTAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format("JWT", "API")

    def authenticate(self, request, payload=False):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0] != settings.AUTH_HEADER_PREFIX:
            return None

        # read header informations
        if len(auth) == 1:
            msg = _('No credentials provided')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Credentials string should not contain spaces')
            raise AuthenticationFailed(msg)

        # authenticate user
        try:
            payload = decode_handler(auth[1])
        except jwt.ExpiredSignature:
            msg = _('Signature has expired')
            raise AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature')
            raise AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        if payload:
            return (user, payload)
        else:
            return (user, auth[1])

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()  # noqa
        username = payload.get('username', None)
        # employee = payload.get('employee', None)

        if not username:
            msg = _('Payload is invalid')
            raise AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(*username)
        except User.DoesNotExist:
            msg = _('User is invalid')
            raise AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User is disabled')
            raise AuthenticationFailed(msg)

        return user
