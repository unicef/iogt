from bs4 import BeautifulSoup
from django.utils.functional import cached_property
from wagtail.images.models import Rendition


class PageUtilsMixin:
    """
    This mixin contains the common properties/utilities shared across most children
    of wagtail.core.models.Page
    """

    @cached_property
    def parent_section(self):
        from .models import Section
        return Section.objects.parent_of(self).type(Section).first()

    @cached_property
    def is_first_content(self):
        from .models import Article, Section, PageLinkPage

        rv = False
        if isinstance(self, (Section, Article, PageLinkPage)):
            parent = self.get_parent().specific
            children = list(parent.get_children().live().specific().order_by('path'))
            index = children.index(self)
            if index == 0 and parent.larger_image_for_top_page_in_list_as_in_v1:
                rv = True

        return rv

    @cached_property
    def get_type(self):
        return self.__class__.__name__.lower()

    def _get_renditions(self, image_id):
        image_urls = []
        for rendition in Rendition.objects.filter(image_id=image_id):
            image_urls.append(rendition.url)
        return image_urls

    def _get_images_from_block(self, value):
        image_urls = []

        tags = BeautifulSoup(value, "html.parser").find_all('embed')
        for tag in tags:
            if tag.attrs['embedtype'] == 'image':
                image_urls += self._get_renditions(tag.attrs['id'])

        return image_urls

    def _get_stream_data_image_urls(self, raw_data):
        image_urls = []

        for block in raw_data:
            if block['type'] == 'image':
                image_urls += self._get_renditions(block['value'])
            if block['type'] == 'paragraph':
                image_urls += self._get_images_from_block(block['value'])
            if block['type'] == 'download':
                image_urls += self._get_images_from_block(block['value'].get('description', ''))

        return image_urls

    @property
    def get_image_urls(self):
        raise NotImplementedError


class TitleIconMixin:
    """
    This mixin is used for duck-typing
    """

    def get_page(self):
        return self

    def get_icon(self):
        class Icon(object):
            url = ''
            is_svg_icon = False
            path = ''

            def __init__(self, url='', is_svg_icon=False):
                self.url = url
                self.is_svg_icon = is_svg_icon

            def __str__(self):
                return f'{self.url}'

        icon = Icon()
        if hasattr(self, 'icon') and self.icon:
            icon = Icon(self.icon.url, True)
            icon.path = self.icon.file.name
        elif hasattr(self, 'image_icon') and self.image_icon:
            icon = Icon(self.image_icon.get_rendition('fill-32x32').url, False)

        return icon
