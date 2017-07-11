#!/usr/bin/python
# ex:set fileencoding=utf-8:

from easy_thumbnails.processors import colorspace
# from easy_thumbnails.processors import autocrop
from easy_thumbnails.processors import scale_and_crop
# from easy_thumbnails.processors import filters
# from easy_thumbnails.processors import background


class BaseFormatter():

    def __init__(self, size=(None, None), poi=(None, None), crop=True, upscale=True, zoom=None, quality=85, **kwargs):
        self.size = size
        self.poi = poi
        self.crop = crop
        self.upscale = upscale
        self.zoom = zoom
        self.quality = quality
        self.kwargs = kwargs

    def render(self, img):
        """
        needs to return an img instance
        """
        raise NotImplementedError


class DefaultFormatter(BaseFormatter):

    def render(self, img):

        img = colorspace(img)
        # img = autocrop(img)

        if self.poi[0] and self.poi[1]:
            source_x, source_y = [float(v) for v in im.size]
            target = (self.poi[0] / source_x, self.poi[1] / source_y)
        else:
            target = None

        img = scale_and_crop(
            self.size,
            crop=self.crop,
            upscale=self.upscale,
            zoom=self.zoom,
            target=target
        )

        # img = filters(img)
        # img = background(img)

        return img
