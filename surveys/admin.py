from django.contrib import admin

from django.contrib import admin

from . models import SurveyPage

from wagtail.contrib.modeladmin.options import(
    ModelAdmin,
    modeladmin_register,

	)


class SurveyPageAdmin(ModelAdmin):
 	model = SurveyPage
 	menu_label = "Surveys"
 	menu_icon  = "group"
 	menu_order = 280
 	add_to_settings_menu = False
 	exclute_from_explorer = False	
 	


modeladmin_register(SurveyPageAdmin)