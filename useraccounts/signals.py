#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.dispatch.dispatcher import Signal


# send on successful login
login_success = Signal(providing_args=['user'])

# send when login failed
login_failed = Signal(providing_args=['user', 'seen'])

# send when the user changes his primary email address
email_changed = Signal(providing_args=['user', 'email'])

# send when the user validates a email address
email_validated = Signal(providing_args=['user', 'email'])

# send when the user validates his email address for the first time
user_validated = Signal(providing_args=['user'])

# send when the user is activated
user_activated = Signal(providing_args=['user'])

# send when the user is deactivated
user_deactivated = Signal(providing_args=['user'])

# send whenever a validation is send
validation_send = Signal(providing_args=['user', 'email', 'stamp', 'crypt', 'skip'])

# send whenever a password restore request is send
password_restore_send = Signal(providing_args=['user', 'email', 'stamp', 'crypt', 'skip'])
