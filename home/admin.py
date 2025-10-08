from django.contrib import admin
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.db.models import Avg, Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import get_language_info

from home.models import ManifestSettings, SVGToPNGMap, Article, ArticleFeedback


class ManifestSettingsAdmin(ModelAdmin):
    model = ManifestSettings
    menu_label = "Manifest Settings"
    menu_icon = "cog"
    add_to_settings_menu = True
    list_display = ("language", "name")
    exclude_from_explorer = False


modeladmin_register(ManifestSettingsAdmin)


@admin.register(SVGToPNGMap)
class SVGToPNGMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'svg_path', 'fill_color', 'stroke_color', 'png_image_file')


class ArticleAdmin(ModelAdmin):
    model = Article
    menu_label = "Article Ratings"
    menu_icon = "form"
    list_display = ("title", "average_rating", "number_of_reviews", "view_feedback_button", "get_locale")
    search_fields = ("title",)
    ordering = ("-average_rating", "-number_of_reviews")  # Sort by rating & reviews in descending order
    def get_locale(self, obj):
        if obj.locale:
            info = get_language_info(obj.locale.language_code)
            return info["name_local"]
        return "-"
    get_locale.short_description = "Locale"
    get_locale.admin_order_field = "locale"
    def view_feedback_button(self, obj):
        """
        Creates a button to view feedback for an article.
        """
        url = reverse("admin_article_feedback", args=[obj.id])
        return format_html('<a class="button button-small" href="{}">View Feedback</a>', url)
    view_feedback_button.short_description = "Feedback"

    def has_add_permission(self, request):
        """
        Hide the 'Add Article' button in the Wagtail admin panel.
        """
        return False  # Prevents adding new articles from this page

modeladmin_register(ArticleAdmin)
