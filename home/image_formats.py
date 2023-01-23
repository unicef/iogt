from django.utils.translation import gettext_lazy as _

from wagtail.images.formats import Format, register_image_format, unregister_image_format, get_image_formats


image_formats = get_image_formats()
for image_format in image_formats:
    unregister_image_format(image_format.name)


register_image_format(Format('fullwidth', _('Full width'), 'richtext-image full-width', 'width-750'))
register_image_format(Format('left', _('Left-aligned'), 'richtext-image left', 'width-750'))
register_image_format(Format('right', _('Right-aligned'), 'richtext-image right', 'width-750'))
register_image_format(Format('original',
                             _('Original Size (Can use LARGE amounts of user data package, not recommended)'),
                             'richtext-image original', 'original'))
