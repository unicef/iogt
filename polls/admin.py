from django.contrib import admin

from django.contrib import admin

from . models import PollPage

from wagtail.contrib.modeladmin.options import(
    ModelAdmin,
    modeladmin_register,

	)


class PollPageAdmin(ModelAdmin):
 	model = PollPage
 	menu_label = "Polls"
 	menu_icon  = "doc-full"
 	menu_order = 290
 	add_to_settings_menu = False
 	exclute_from_explorer = False	
 	


modeladmin_register(PollPageAdmin)