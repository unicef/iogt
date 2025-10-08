from wagtail_modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from .models import InteractiveChannel


class InteractiveChannelAdmin(ModelAdmin):
    model = InteractiveChannel
    menu_label = "Interactive RapidPro Channels"
    menu_icon = "tag"
    index_template_name = "interactive/interactivechannel/index.html"


class InteractiveGroup(ModelAdminGroup):
    menu_label = "Interactive"
    menu_icon = "tag"
    items = (InteractiveChannelAdmin,)


modeladmin_register(InteractiveGroup)
