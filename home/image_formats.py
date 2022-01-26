from django.utils.translation import gettext_lazy as _

from wagtail.images.formats import Format, register_image_format, unregister_image_format, get_image_formats


image_formats = get_image_formats()
for image_format in image_formats:
    unregister_image_format(image_format.name)


register_image_format(Format('fullwidth', _('Full width'), 'richtext-image full-width', 'width-360'))
register_image_format(Format('left', _('Left-aligned'), 'richtext-image left', 'width-360'))
register_image_format(Format('right', _('Right-aligned'), 'richtext-image right', 'width-360'))
