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
    def get_type(self):
        return self.__class__.__name__.lower()

    def get_url(self):
        return self.url


class TitleIconMixin:
    """
    This mixin is used for duck-typing
    """

    def get_page(self):
        return self

    def get_icon_url(self):
        from wagtail.images.views.serve import generate_image_url

        class Icon(object):
            url = ''
            is_svg_icon = False

            def __init__(self, url='', is_svg_icon=False):
                self.url = url
                self.is_svg_icon = is_svg_icon

        icon = Icon()
        if hasattr(self, 'icon') and self.icon:
            icon = Icon(self.icon.url, True)
        elif hasattr(self, 'image_icon') and self.image_icon:
            icon = Icon(generate_image_url(self.image_icon, 'fill-32x32'), False)

        return icon
