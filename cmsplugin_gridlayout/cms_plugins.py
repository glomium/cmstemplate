#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Section
from .models import Row
from .models import Column


class SectionPlugin(CMSPluginBase):
    model = Section
    module = _("Layout")
    name = _("Section")
    render_template = "cmsplugin_gridlayout/section.html"
    # child_classes = ['RowPlugin', 'EmbedPlugin', 'TextPlugin', 'ImagePlugin', 'MediaObjectPlugin', "ButtonPlugin", "MailformPlugin"]
    allow_children = True
    require_parent = False

    def render(self, context, instance, placeholder):
        context['css'] = instance.get_css()
        context['instance'] = instance
        return context
plugin_pool.register_plugin(SectionPlugin)


class RowPlugin(CMSPluginBase):
    model = Row
    module = _("Layout")
    name = _("Row")
    render_template = "cmsplugin_gridlayout/row.html"
    require_parent = True
    allow_children = True
    child_classes = ['ColumnPlugin']

    # if "cmsplugin_filer_image" in settings.INSTALLED_APPS:
    #     child_classes.append("FilerImagePlugin")

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context
plugin_pool.register_plugin(RowPlugin)


class ColumnPlugin(CMSPluginBase):
    model = Column
    module = _("Layout")
    name = _("Column")
    render_template = "cmsplugin_gridlayout/column.html"
    parent_classes = ['RowPlugin']
    allow_children = True

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['css'] = instance.get_css()
        return context
plugin_pool.register_plugin(ColumnPlugin)
