from wagtail.contrib.modeladmin.options import (
    ModelAdminGroup, ModelAdmin, modeladmin_register
)
from .models import CrankyUncleChannel


class CrankyUncleChannelAdmin(ModelAdmin):
    model = CrankyUncleChannel
    menu_label = 'Cranky Uncle Channels'
    menu_icon = 'tag'
    # index_template_name = ''


class CrankyUncleGroup(ModelAdminGroup):
    menu_label = 'Cranky Uncle'
    menu_icon = 'tag'
    items = (CrankyUncleChannelAdmin,)


modeladmin_register(CrankyUncleGroup)
