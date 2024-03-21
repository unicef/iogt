from wagtail.contrib.modeladmin.options import (
    ModelAdminGroup, ModelAdmin, modeladmin_register
)
from .models import InteractiveChannel


class InteractiveChannelAdmin(ModelAdmin):
    model = InteractiveChannel
    menu_label = 'Interactive RapidPro Channels'
    menu_icon = 'tag'


class InteractiveGroup(ModelAdminGroup):
    menu_label = 'Interactive'
    menu_icon = 'tag'
    items = (InteractiveChannelAdmin,)


modeladmin_register(InteractiveGroup)
