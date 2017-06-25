# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator


class AngularTemplateView(TemplateView):
    def get_template_names(self):
        if "path" not in self.kwargs or len(self.kwargs["path"]) < 6 or self.kwargs["path"][-5:] != ".html":
            raise Http404

        return ["component/" + self.kwargs["path"]]

    @method_decorator(cache_page(86400))  # 24h
    def get(self, *args, **kwargs):
        return super(AngularTemplateView, self).get(*args, **kwargs)
