#!/usr/bin/python
# ex:set fileencoding=utf-8:

from django.apps import apps
from django.apps import AppConfig
from django.core.checks import register
from django.core.checks import Error


class Config(AppConfig):
    name = 'mosquitto'
    label = 'mosquitto'
    verbose_name = "MQTT Manager"


# Checks
@register()
def checks(app_configs, **kwargs):  # noqa
    errors = []

    if not apps.is_installed('django.contrib.admin'):  # pragma: no cover
        errors.append(Error(
            'django.contrib.admin not found',
            hint="Put 'django.contrib.admin' in your INSTALLED_APPS setting",
            id='emailhosting.E001',
        ))

    return errors
