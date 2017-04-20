import markdown

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Markdown
from .utils.urlize import UrlizeExtension
from .utils.checklist import ChecklistExtension
from .utils.strikethrough import StrikeThroughExtension


class MarkdownCMSPlugin(CMSPluginBase):
    model = Markdown
    name = _('Markdown')
    render_template = 'cmsplugin_markdown/plugin.html'

    def render(self, context, instance, placeholder):
        context['raw'] = instance.raw_text

        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.toc',
                UrlizeExtension(),
                StrikeThroughExtension(),
                ChecklistExtension(),
                'markdown.extensions.admonition',
                'markdown.extensions.codehilite',
                'markdown.extensions.fenced_code',
                'markdown.extensions.smart_strong',
                'markdown.extensions.sane_lists',
                'markdown.extensions.smarty',
                'markdown.extensions.table',
            ],
            output_format="html5",
            save_mode='escape',
            smart_emphasis=True,
            lazy_ol=True,
        )

        context['html'] = mark_safe(md.convert(instance.raw_text))
        context['show_toc'] = instance.show_toc
        context['toc'] = mark_safe(md.toc)
        return context


plugin_pool.register_plugin(MarkdownCMSPlugin)
