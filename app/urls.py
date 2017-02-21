# -*- coding: utf-8 -*-
"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

from django.contrib.sitemaps.views import index as sitemaps_index
from django.contrib.sitemaps.views import sitemap as sitemaps_sitemap
from django.views.static import serve

from importlib import import_module
from collections import OrderedDict


SITEMAPS = {}
for key, modulepath in OrderedDict(sorted(getattr(settings, 'CMSTEMPLATE_SITEMAPS', {}).items())).items():
    module_path, class_name = modulepath.rsplit('.', 1)
    module = import_module(module_path)
    SITEMAPS[key] = getattr(module, class_name)


urlpatterns = [
    url(r'^sitemap\.xml$', sitemaps_index, {'sitemaps': SITEMAPS}),
    url(r'^sitemap-(?P<section>\w+)\.xml$', sitemaps_sitemap, {'sitemaps': SITEMAPS}),
]


urlpatterns += i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^', include('cms.urls')),
    prefix_default_language=getattr(settings, "USE_I18N", False),
)

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
