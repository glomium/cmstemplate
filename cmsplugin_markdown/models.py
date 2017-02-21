from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible


@python_2_unicode_compatible
class Markdown(CMSPlugin):
    raw_text = models.TextField(_("Text"))
    show_toc = models.BooleanField(_("Table of Contents"), default=False)

    def __str__(self):
        if len(self.raw_text) > 43:
            return self.raw_text[:40] + '...'
        return self.raw_text
