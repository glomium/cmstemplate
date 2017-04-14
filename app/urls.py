# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

from django.contrib.sitemaps.views import index as sitemaps_index
from django.contrib.sitemaps.views import sitemap as sitemaps_sitemap
from django.views.static import serve

from rest_framework.documentation import include_docs_urls

from importlib import import_module
from collections import OrderedDict

from .routers import router


SITEMAPS = {}
for key, modulepath in OrderedDict(sorted(getattr(settings, 'CMSTEMPLATE_SITEMAPS', {}).items())).items():
    module_path, class_name = modulepath.rsplit('.', 1)
    module = import_module(module_path)
    SITEMAPS[key] = getattr(module, class_name)


urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^apidocs/', include_docs_urls(title="API", description=None)),
    url(r'^sitemap\.xml$', sitemaps_index, {'sitemaps': SITEMAPS}),
    url(r'^sitemap-(?P<section>\w+)\.xml$', sitemaps_sitemap, {'sitemaps': SITEMAPS}),
]


if getattr(settings, "USE_I18N", False):
    urlpatterns += i18n_patterns(
        url(r'^admin/', admin.site.urls),
        url(r'^', include('cms.urls')),
        prefix_default_language=True,
    )
else:
    urlpatterns += [
        url(r'^admin/', admin.site.urls),
        url(r'^', include('cms.urls')),
    ]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
