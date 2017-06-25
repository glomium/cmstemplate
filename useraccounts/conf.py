#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings as djsettings


class Settings(object):

    PREFIX = "USERACCOUNTS"
    DEFAULTS = {
    
        # Enable login via...
        "LOGIN_EMAIL": True,
        "LOGIN_USERNAME": True,

        # Login security
        "CACHE_PREFIX": "useraccounts",
        "INTERNAL_IPS": djsettings.INTERNAL_IPS,

        "THROTTLE_IP": True,
        "THROTTLE_IP_COUNT": 25,
        "THROTTLE_IP_INTERVAL": 5,

        "THROTTLE_USER": True,
        "THROTTLE_USER_COUNT": 5,
        "THROTTLE_USER_INTERVAL": 3,

        "THROTTLE_SIGNAL_TIMEOUT": 180,

        # Email validation
        "VALIDATION_SALT": "useraccounts.email",
        "VALIDATION_TIMEOUT": 72,
        "VALIDATION_SEND_MAIL": True,
        "VALIDATION_TEMPLATE_HTML": None,
        "VALIDATION_TEMPLATE_PLAIN": "useraccounts/email_validation.txt",
        "VALIDATION_TEMPLATE_SUBJECT": "useraccounts/email_validation.subject",

        # Password restore
        "RESTORE_SALT": "useraccounts.restore",
        "RESTORE_TIMEOUT": 24,
        "RESTORE_SEND_MAIL": True,
        "RESTORE_TEMPLATE_HTML": None,
        "RESTORE_TEMPLATE_PLAIN": "useraccounts/email_restore.txt",
        "RESTORE_TEMPLATE_SUBJECT": "useraccounts/email_restore.subject",

        # resolve views
        "RESTORE_AUTOLOGIN": True,
        "RESOLVE_EMAIL_VALIDATE": None,
        "RESOLVE_PASSWORD_RESTORE": None,

        "REDIRECT_EMAIL_CREATE": None,
        "REDIRECT_EMAIL_VALIDATE": None,
        "REDIRECT_EMAIL_UPDATE": None,
        "REDIRECT_EMAIL_DELETE": None,
        "REDIRECT_EMAIL_RESEND": None,

        "REDIRECT_RESTORE_CREATE": None,
        "REDIRECT_RESTORE_SUCCESS": djsettings.LOGIN_REDIRECT_URL,

        "REDIRECT_CHANGE_SUCCESS": djsettings.LOGIN_REDIRECT_URL,

        "AUTH_EXPIRATION_DELTA": 300,
        "AUTH_HEADER_PREFIX": "JWT",
        "AUTH_SECRET_KEY": djsettings.SECRET_KEY,
        "AUTH_ISSUER": None,
        "AUTH_AUDIENCE": None,
        "AUTH_ALGORITHMS": ["HS256"],

        # username
        "USERNAME_VALIDATORS": [
            {'NAME': 'useraccounts.validators.UsernameValidator'}
        ],
    }

    def __init__(self):
        for key, value in self.DEFAULTS.items():
            variable = "%s_%s" % (self.PREFIX, key)
            if not hasattr(djsettings, variable):
                setattr(djsettings, variable, value)
            setattr(self, key, getattr(djsettings, variable))


settings = Settings()
