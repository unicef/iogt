# -*- coding: utf-8 -*-
"""Monkey patch wagtailimages_tags.image tag to resolve specs from a context variable."""

from django import template
from django.utils.functional import cached_property

from wagtail.images.models import Filter
from wagtail.images.shortcuts import get_rendition_or_not_found

register = template.Library()

class ImageNodeReplace(template.Node):
    def __init__(self, image_expr, filter_spec, output_var_name=None, attrs={}):
        self.image_expr = image_expr
        self.output_var_name = output_var_name
        self.attrs = attrs
        self.filter_spec = filter_spec
        self.resolved_filter_spec = None

    @cached_property
    def filter(self):
        return Filter(spec=self.resolved_filter_spec)

    def render(self, context):
        try:
            image = self.image_expr.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not image:
            if self.output_var_name:
                context[self.output_var_name] = None
            return ''

        if not hasattr(image, 'get_rendition'):
            raise ValueError("image tag expected an Image object, got %r" % image)

        # resolve filter_specs
        filter_specs = self.filter_spec.split("|")
        resolved_filter_specs = []
        for filter_spec in filter_specs:
            if filter_spec == "original" or "-" in filter_spec:
                resolved_filter_specs.append(filter_spec)
                continue
            try:
                variable = template.Variable(filter_spec).resolve(context)
                resolved_filter_specs.append(variable)
            except template.VariableDoesNotExist:
                resolved_filter_specs.append(filter_spec)
        self.resolved_filter_spec = "|".join(resolved_filter_specs)

        rendition = get_rendition_or_not_found(image, self.filter)

        if self.output_var_name:
            # return the rendition object in the given variable
            context[self.output_var_name] = rendition
            return ''
        else:
            # render the rendition's image tag now
            resolved_attrs = {}
            for key in self.attrs:
                resolved_attrs[key] = self.attrs[key].resolve(context)
            return rendition.img_tag(resolved_attrs)

# Monkey patch
from wagtail.images.templatetags import wagtailimages_tags
wagtailimages_tags.ImageNode = ImageNodeReplace
