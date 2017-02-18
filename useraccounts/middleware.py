# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.cache import patch_vary_headers


class PrivacyMiddleware(object):
    """
    Sets request.DNT to True or False based on the presence of the
    DNT HTTP header and reads the cookie_law cookies and stores the
    information in the request.
    """

    def process_request(self, request):
        if request.META.get('HTTP_DNT') == '1':
            request.DNT = True
        else:
            request.DNT = False

        request.privacy_settings = {
            'accepted': bool(request.COOKIES.get('cookie_law_accepted', request.user.is_authenticated())),
            'performance': bool(request.COOKIES.get('performance_tracking', True)),
            'targeting': bool(request.COOKIES.get('targeting_tracking', not request.DNT)),
        }

    def process_response(self, request, response):
        # content may depend on DNT
        patch_vary_headers(response, ('DNT',))
        return response
