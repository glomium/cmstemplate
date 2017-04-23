#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Embed


class EmbedPlugin(CMSPluginBase):
    model = Embed
    # module = _("Embed")
    name = _("Embed")
    render_template = "cmsplugin_embed/embed.html"
    # parent_classes = ['ColumnPlugin', 'SectionPlugin']
    allow_children = False

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context
plugin_pool.register_plugin(EmbedPlugin)
