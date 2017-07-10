#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.http import FileResponse
from django.views.generic import View

from mimetypes import MimeTypes
from PIL import Image

from .conf import MIME_TYPES_IMAGES

import os


class ImageManagerView(View):

    def get(self, request, path=None, *args, **kwargs):

        full_path = path

        if not path:
            raise Http404

        # TODO: read x, y from database
        # TODO: dont remove x, y from name unless image changes also delete cache
        # read formatter, breakpoint, x and y from image path
        try:
            formatter, breakpoint, path = path.split('/', 2)
            tmp, x, y = path.rsplit('_', 2)
            y, ext = y.split('.', 1)
            x = int(x)
            y = int(y)
            path = tmp + '.' + ext
        except ValueError:
            return HttpResponse(status=400)

        filepath = os.path.join(settings.FILEMANAGER_STORAGE_ROOT, path)
        mime_type = MimeTypes().guess_type(filepath)[0]

        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise Http404("Could not find %s" % path)

        if not mime_type in MIME_TYPES_IMAGES:
            return HttpResponse(status=400)

        cachepath = os.path.join(settings.FILEMANAGER_CACHE_ROOT, full_path)

        # TODO: check formatter

        # TODO: check breakpoint

        # create directories
        if not os.path.isdir(os.path.dirname(cachepath)):
            os.makedirs(os.path.dirname(cachepath))

        filename = os.path.basename(cachepath)

        # TODO USE FORMATTER
        img = Image.open(filepath)
        img.thumbnail((x, y))
        img.save(cachepath)

        response = FileResponse(open(cachepath, 'rb'))
        response['Content-Type'] = mime_type
        response['Content-Length'] = os.path.getsize(cachepath)

        return response


class FileManagerView(View):
    """
    """

    def get(self, request, path=None, *args, **kwargs):

        if not path:
            raise Http404

        filepath = os.path.join(settings.FILEMANAGER_STORAGE_ROOT, path)

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
        """
        """

        mime_type = MimeTypes().guess_type(filepath)[0]

        download = "d" in request.GET

        sendtype = getattr(settings, "FILEMANAGER_SENDTYPE", None)
        filename = os.path.basename(filepath)
        fileurl = os.path.join(settings.FILEMANAGER_STORAGE_URL, path)

        response = None

        # Nginx (TODO: untested)
        if sendtype == "xaccel" and not settings.DEBUG:
            response = HttpResponse()
            response['X-Accel-Redirect'] = fileurl

        # Lighthttpd or Apache with mod_xsendfile (TODO: untested)
        if sendtype == "xsendfile" and not settings.DEBUG:
            response = HttpResponse()
            response['X-Sendfile'] = filepath

        if not response:
            # Serve file with django
            response = FileResponse(open(filepath, 'rb'))

            if mime_type:
                response['Content-Type'] = mime_type

            response['Content-Length'] = os.path.getsize(filepath)

        if download:
            response['Content-Type'] = 'application/force-download'
            response['Content-Disposition'] = 'inline; filename=%s' % filename

        return response

    # PUT to create files
    def put(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)

    # DELETE files
    def delete(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)
