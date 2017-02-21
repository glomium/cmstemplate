#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

import markdown

from ..utils.urlize import UrlizeExtension
from ..utils.checklist import ChecklistExtension
from ..utils.strikethrough import StrikeThroughExtension

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(text):
    """
    """
    if not text:
        return ''
    return mark_safe(markdown.markdown(
        text,
        extensions=[
            UrlizeExtension(),
            StrikeThroughExtension(),
            ChecklistExtension(),
            'smart_strong',
            'sane_lists',
            'smarty',
            'fenced_code',
            'codehilite',
        ],
        output_format="html5",
        save_mode='escape',
        smart_emphasis=True,
        lazy_ol=True,
    ))
markdown_filter.is_safe = True
