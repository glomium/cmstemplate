#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

import jwt

from .conf import settings


def get_payload(user):
    payload = {
        'user': {
            'id': user.pk,
            'name': user.username,
            'full_name': user.get_full_name() or None,
            'email': user.email or None,
        },
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=settings.AUTH_EXPIRATION_DELTA),
    }

    if settings.AUTH_AUDIENCE is not None:
        payload['aud'] = settings.AUTH_AUDIENCE

    if settings.AUTH_ISSUER is not None:
        payload['iss'] = settings.AUTH_ISSUER

    return payload

'''
def payload_update(payload):
    payload.update({
        'exp': datetime.utcnow() + timedelta(seconds=settings.AUTH_EXPIRATION_DELTA),
    })
    return payload
'''

def decode_handler(token):
    return jwt.decode(
        token,
        settings.AUTH_SECRET_KEY,
        audience=settings.AUTH_AUDIENCE,
        issuer=settings.AUTH_ISSUER,
        algorithms=settings.AUTH_ALGORITHMS,
    )


def encode_handler(payload):
    return jwt.encode(
        payload,
        settings.AUTH_SECRET_KEY,
        algorithm=settings.AUTH_ALGORITHMS[0],
    ).decode('utf-8')
