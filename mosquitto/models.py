#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


import logging


logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class ACL(models.Model):
    """
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)

    topic = models.CharField(_("Topic"), max_length=64, null=False, blank=False)

    permission = models.PositiveSmallIntegerField(
        _("Permission"),
        null=False,
        blank=False,
        choices=(
            (1, _("Subscribe")),
            (2, _("Subscribe and Publish")),
        ),
        default=1,
        db_index=True,
    )

    active = models.BooleanField(_("Is active"), default=True, db_index=True)

    def __str__(self):
        return '%s' % (self.topic)

    class Meta:
        verbose_name = _('Access Control List')
        verbose_name_plural = _('Access Control Lists')
        unique_together = (
            ('user', 'topic'),
        )
