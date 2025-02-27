from django.contrib import admin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from django.db.models import Avg
from django.utils.html import format_html
from django.urls import reverse

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
    list_display = ("title", "average_rating", "view_feedback_button")
    search_fields = ("title",)

    def average_rating(self, obj):
        avg_rating = obj.feedbacks.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        return round(avg_rating, 1)
    average_rating.short_description = "Average Rating"

    def view_feedback_button(self, obj):
        url = reverse("admin_article_feedback", args=[obj.id])  # Corrected URL
        return format_html('<a class="button button-small" href="{}">View Feedback</a>', url)
    view_feedback_button.short_description = "Feedback"

modeladmin_register(ArticleAdmin)
