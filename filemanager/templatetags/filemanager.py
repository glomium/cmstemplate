from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def thumbnail(obj):

    url, ext = obj.url.rsplit('.', 1)

    if obj.subject_location:
        x, y = obj.subject_location.split(',')
    else:
        x = 0
        y = 0

    return '%s_%s_%s_%s.%s' % (
        url,
        obj.pk,
        x,
        y,
        ext,
    )
