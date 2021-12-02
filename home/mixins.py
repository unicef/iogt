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


class TitleIconMixin:
    """
    This mixin is used for footers duck-typing
    """

    def get_page(self):
        return self

    def get_icon_url(self):
        return getattr(getattr(self, 'icon', object), 'url', '')
