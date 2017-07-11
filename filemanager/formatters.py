#!/usr/bin/python
# ex:set fileencoding=utf-8:


class BaseFormatter():

    def __init__(self, size=(None, None), poi=(None, None), crop=True, quality=85, **kwargs):
        self.size = size
        self.poi = poi
        self.crop = crop
        self.quality = quality
        self.kwargs = kwargs

    def render(self, img):
        """
        needs to return an img instance
        """
        raise NotImplementedError


class DefaultFormatter(BaseFormatter):

    def render(self, img):
        img.thumbnail(self.size)
        return img
