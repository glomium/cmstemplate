#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.http import FileResponse
from django.views.generic import View

from mimetypes import MimeTypes

import os


class FileManagerView(View):

    def get(self, request, path=None, *args, **kwargs):
        if not path:
            raise Http404

        filepath = os.path.join(settings.FILEMANAGER_ROOT, path)

        if not os.path.exists(filepath):
            raise Http404("Could not find %s" % path)

        if os.path.isfile(filepath):
            return self.get_file(request, path, filepath)

        if os.path.isdir(filepath):
            return self.get_dir(request, path, filepath)

        return HttpResponse(status=403)

    def get_dir(self, request, path, filepath):
        # TODO
        return HttpResponse(status=500)

    def get_file(self, request, path, filepath):

        mime_type = MimeTypes().guess_type(filepath)[0]

        sendtype = getattr(settings, "FILEMANAGER_SENDTYPE", None)
        filename = os.path.basename(filepath)
        fileurl = os.path.join(settings.FILEMANAGER_URL, path)

        # Nginx (TODO: untested)
        if sendtype == "xaccel" and not settings.DEBUG:
            response = HttpResponse()
            # response['Content-Type'] = 'application/force-download'
            # response['Content-Disposition'] = 'inline; filename=%s' % filename
            response['X-Accel-Redirect'] = fileurl
            return response

        # Lighthttpd or Apache with mod_xsendfile (TODO: untested)
        if sendtype == "xsendfile" and not settings.DEBUG:
            response = HttpResponse()
            # response['Content-Type'] = 'application/force-download'
            # response['Content-Disposition'] = 'inline; filename=%s' % filename
            response['X-Sendfile'] = filepath
            return response

        # Serve file with django
        response = FileResponse(open(filepath, 'rb'))

        if mime_type:
            response['Content-Type'] = mime_type

        response['Content-Length'] = os.path.getsize(filepath)

        # response['Content-Disposition'] = 'inline; filename=%s' % filename

        return response

    # PUT to create files
    def put(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)

    # DELETE files
    def delete(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)
