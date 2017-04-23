# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

@python_2_unicode_compatible
class Embed(CMSPlugin):
    """
    """
    source = models.CharField(
        _('Source'),
        max_length=255,
        blank=False,
        null=True,
    )
    allow_fullscreen = models.BooleanField(
        _('Allow fullscreen'),
        default=False,
    )

    ratio = models.CharField(
        _('Ratio'),
        max_length=5,
        blank=False,
        null=False,
        choices=(
            ('21by9', _('21:9')),
            ('16by9', _('16:9')),
            ('4by3', _('4:3')),
            ('1by1', _('1:1')),
        ),
        default='16by9',
    )

    def __str__(self):
        if self.source:
            return '%s' % self.source
        else:
            return 'None'
