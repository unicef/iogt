from django.utils.functional import cached_property


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
