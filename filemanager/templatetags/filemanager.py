from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def thumbnail(obj, cls, breakpoint):

    url, ext = obj.url.rsplit('.', 1)

    if obj.subject_location:
        x, y = obj.subject_location.split(',')
    else:
        x = 0
        y = 0

    return '%s%s/%s%s_%s_%s_%s.%s' % (
        settings.FILEMANAGER_CACHE_URL,
        cls,
        breakpoint,
        url,
        obj.pk,
        x,
        y,
        ext,
    )
