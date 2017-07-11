#!/usr/bin/python
# ex:set fileencoding=utf-8:

from easy_thumbnails.utils import exif_orientation
from easy_thumbnails.processors import colorspace
# from easy_thumbnails.processors import autocrop
from easy_thumbnails.processors import scale_and_crop
# from easy_thumbnails.processors import filters
# from easy_thumbnails.processors import background


class BaseFormatter():

    def __init__(self, size=(None, None), poi=(None, None), crop=True, upscale=True, zoom=None, **kwargs):
        self.size = size
        self.poi = poi
        self.crop = crop
        self.upscale = upscale
        self.zoom = zoom
        self.kwargs = kwargs

    def render(self, img):
        """
        needs to return an img instance
        """
        raise NotImplementedError


class DefaultFormatter(BaseFormatter):

    def render(self, img):

        img = exif_orientation(img)

        img = colorspace(img)
        # img = autocrop(img)

        if self.poi[0] and self.poi[1]:
            source_x, source_y = [float(v) for v in img.size]
            target = (self.poi[0] / source_x, self.poi[1] / source_y)

            for i in range(2):
                if target[i] > 1.:
                    target[i] = 1
        else:
            target = None

        img = scale_and_crop(
            img,
            self.size,
            crop=self.crop,
            upscale=self.upscale,
            zoom=self.zoom,
            target=target
        )

        # img = filters(img)
        # img = background(img)

        return img
