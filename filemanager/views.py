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

import importlib
import logging
import os

try:
    from filer.models import Image as FilerImage
    FILER = True
except ImportError:
    FILER = False


logger = logging.getLogger(__name__)


class ImageManagerView(View):

    def get(self, request, path=None, *args, **kwargs):

        full_path = path

        if not path:
            raise Http404

        try:
            formatter, breakpoint, path = path.split('/', 2)
        except ValueError:
            return HttpResponse(status=400)

        # TODO: read x, y from database
        # TODO: dont remove x, y from name unless image changes also delete cache
        # read formatter, breakpoint, x and y from image path
        try:
            tmp, pk, x, y = path.rsplit('_', 3)
            y, ext = y.split('.', 1)
            pk = int(pk)
            x = int(x)
            y = int(y)
            path = tmp + '.' + ext
        except ValueError:
            return HttpResponse(status=400)

        # TODO: if we have an own file-system manager we'll use the path
        #       to obtain the object. sending the images pk wont be neccecary
        #       anymore. at that case we'll drop the support for filer.
        # TODO: compatability layer with filer
        if pk:

            try:
                image = FilerImage.objects.get(pk=pk)
            except FilerImage.DoesNotExist:
                raise Http404

            if image.file.url[1:] != path:
                raise Http404

            filepath = image.file.path

            if image.subject_location:
                if image.subject_location != '%s,%s' % (x, y):
                    raise Http404

        # Load image from storage and create cached thumbnail
        else:
            filepath = os.path.join(settings.FILEMANAGER_STORAGE_ROOT, path)

        mime_type = MimeTypes().guess_type(filepath)[0]

        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise Http404("Could not find %s" % path)

        if mime_type not in MIME_TYPES_IMAGES:
            return HttpResponse(status=400)

        cachepath = os.path.join(settings.FILEMANAGER_CACHE_ROOT, full_path)

        formatters = getattr(settings, "FILEMANAGER_FORMATTERS", {})

        # check formatter
        if formatter not in formatters:
            logger.critical("formatter not found in formatters")
            return HttpResponse(status=500)

        try:
            breakpoints = formatters[formatter]["breakpoints"]
            quality = formatters[formatter].get("quality", 85)
            formatter_module_name, formatter_class_name = formatters[formatter]["class"].rsplit('.', 1)
            formatter_module = importlib.import_module(formatter_module_name)
            formatter_class = getattr(formatter_module, formatter_class_name)

        except (KeyError, ValueError, ImportError, AttributeError):
            logger.exception("Error in loading formatter")
            return HttpResponse(status=500)

        # check breakpoint
        if breakpoint not in breakpoints:
            return HttpResponse(status=500)

        # create directories
        if not os.path.isdir(os.path.dirname(cachepath)):
            os.makedirs(os.path.dirname(cachepath))

        formatter_instance = formatter_class(
            size=breakpoints[breakpoint],
            poi=(x or None, y or None),
            **formatters[formatter]
        )

        img = formatter_instance.render(Image.open(filepath))

        if mime_type == "image/jpeg":
            img.save(cachepath, quality=quality, optimize=1)
        else:
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

        # Nginx
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

    # POST to update files
    def post(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)

    # DELETE files
    def delete(self, request, path, *args, **kwargs):
        # TODO
        return HttpResponse(status=500)
