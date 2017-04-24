# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from cms.models import CMSPlugin


# TODO generate grid from settings
GRID = (
    ('', _('Use default')),
    ('1', _('1 Span')),
    ('2', _('2 Span')),
    ('3', _('3 Span')),
    ('4', _('4 Span')),
    ('5', _('5 Span')),
    ('6', _('6 Span')),
    ('7', _('7 Span')),
    ('8', _('8 Span')),
    ('9', _('9 Span')),
    ('10', _('10 Span')),
    ('11', _('11 Span')),
    ('12', _('12 Span')),
)

GRID_HIDDEN = (
    ('', _('Always visible')),
    ('hidden-sm-down', _('hidden-sm-down')),
    ('hidden-sm-up', _('hidden-sm-up')),
    ('hidden-md-down', _('hidden-md-down')),
    ('hidden-md-up', _('hidden-md-up')),
    ('hidden-lg-down', _('hidden-lg-down')),
    ('hidden-lg-up', _('hidden-lg-up')),
)


@python_2_unicode_compatible
class Section(CMSPlugin):
    """
    """
    CONTAINER_FLUID = 'f'
    CONTAINER_FIXED = 'c'

    name = models.CharField(
        _('Name'),
        max_length=200,
        blank=True,
        null=True,
    )

    slug = models.SlugField(
        _('Slug'),
        max_length=200,
        blank=True,
        null=True,
    )

    # in_navigation = models.BooleanField(
    #     _('In navigation?'),
    #     default=False,
    #     help_text="has no effect - yet",  # TODO
    # )

    container = models.CharField(
        _('Container'),
        max_length=1,
        blank=True,
        null=True,
        choices=(
            (CONTAINER_FIXED, _('Fixed')),
            (CONTAINER_FLUID, _('Fluid')),
        ),
        default=CONTAINER_FIXED,
    )

    css = models.CharField(
        _('CSS'),
        max_length=200,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.slug or 'Plugin'

    def get_container(self):
        if self.container == self.CONTAINER_FIXED:
            return 'container'
        elif self.container == self.CONTAINER_FLUID:
            return 'container-fluid'
        return None

    def get_css(self):
        data = []
        # if self.background: data.append(self.background)
        if self.css: data.append(self.css)
        return ' '.join(data)


@python_2_unicode_compatible
class Row(CMSPlugin):
    """
    """
    css = models.CharField(
        _('Additional class'),
        default='',
        max_length=40,
        blank=True,
        null=True,
    )

    def __str__(self):
        num_cols = self.get_children().count()
        return ungettext_lazy('with {0} column', 'with {0} columns', num_cols).format(num_cols)


@python_2_unicode_compatible
class Column(CMSPlugin):
    """
    """
    xs = models.CharField(
        _('Phone'),
        choices=GRID,
        default=GRID[-1][0],
        max_length=2,
        blank=True,
        null=True,
    )
    sm = models.CharField(
        _('Tablet'),
        choices=GRID,
        default='',
        max_length=2,
        blank=True,
        null=True,
    )
    md = models.CharField(
        _('Laptop'),
        choices=GRID,
        default='',
        max_length=2,
        blank=True,
        null=True,
    )
    lg = models.CharField(
        _('Desktop'),
        choices=GRID,
        default='',
        max_length=2,
        blank=True,
        null=True,
    )
    xl = models.CharField(
        _('Large Desktop'),
        choices=GRID,
        default='',
        max_length=2,
        blank=True,
        null=True,
    )
    hidden = models.CharField(
        _('Hide Column'),
        choices=GRID_HIDDEN,
        default='',
        max_length=20,
        blank=True,
        null=True,
    )
    css = models.CharField(
        _('Additional class'),
        default='',
        max_length=40,
        blank=True,
        null=True,
    )

    def get_css(self):
        data = [self.xs]
        if self.sm: data.append(self.sm)
        if self.md: data.append(self.md)
        if self.lg: data.append(self.lg)
        if self.xl: data.append(self.xl)
        if self.hidden: data.append(self.hidden)
        if self.css: data.append(self.css)
        return ' '.join(data)

    def __str__(self):
        return self.get_css()
