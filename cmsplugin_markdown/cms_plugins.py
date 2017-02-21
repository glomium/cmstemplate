"""Implementation of CMSPluginBase class for ``cmsplugin-markdown``."""
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import Markdown


class MarkdownCMSPlugin(CMSPluginBase):
    model = Markdown
    name = _('Markdown')
    render_template = 'cmsplugin_markdown/plugin.html'
    # change_form_template = 'cmsplugin_markdown/change_form.html'

    def render(self, context, instance, placeholder):
        context['text'] = instance.raw_text
        return context


plugin_pool.register_plugin(MarkdownCMSPlugin)
