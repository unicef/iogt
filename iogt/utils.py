from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from wagtail.admin.action_menu import ActionMenuItem
from django.urls import path, reverse
from django.utils.html import format_html_join, format_html
from questionnaires.models import Survey
from home.models import Article
from wagtail.models import Site, Page
from wagtail.admin import messages
from user_notifications.tasks import send_app_notifications
from wagtail.contrib.modeladmin.helpers import AdminURLHelper


def has_md5_hash(name):
    return bool(settings.HAS_MD5_HASH_REGEX.search(name))


class NotifyAndPublishMenuItem(ActionMenuItem):
    label = "Notify & Publish"
    name = "notify_and_publish"

    def __init__(self,  order=100, allowed_models=None):
        super().__init__(order=order)
        if allowed_models is None:
            self.allowed_models = tuple()
        else:
            # Handle single class passed directly
            self.allowed_models = (allowed_models,)

    def is_shown(self, context):  # ✅ Correct for Wagtail 3.2
        page = context.get("page")
        return isinstance(getattr(page, "specific", page), self.allowed_models)

    def render_html(self, context):
        page = context["page"]
        url = reverse("notify_and_publish", args=[page.id])
        return format_html(
            '<a href="{}" class="button action-warning">'
                '<span class="icon icon-mail"></span> {}'
            '</a>',
                url,
                self.label,
        )


# shared view
@staff_member_required
def notify_and_publish_view(request, page_id):
    page = Page.objects.get(id=page_id).specific
    revision = page.save_revision(user=request.user)
    revision.publish()
    if isinstance(page, Survey):
        full_url = get_site_for_locale(page)
        send_app_notifications.delay(page.id, full_url, 'survey')
        messages.success(request, f"Survey '{page.title}' published and notified.")

    elif isinstance(page, Article):
        full_url = get_site_for_locale(page)
        send_app_notifications.delay(page.id, full_url, 'article')
        messages.success(request, f"Article '{page.title}' published and notified.")

    else:
        messages.error(request, "Not a valid Survey or Article page.")

    modeladmin_url = AdminURLHelper(type(page))
    return redirect(modeladmin_url.index_url)


def get_site_for_locale(instance):
    """
    Return the Wagtail Site object matching the given locale.
    """
    for site in Site.objects.all():
        if site.root_page.locale.language_code == instance.locale.language_code:
            if not site:
                print("No matching site for locale:", instance.locale)
                return
            relative = instance.relative_url(site)
            if not relative:
                print("Could not get relative URL for instance.")
                return
            full_url = settings.WAGTAILADMIN_BASE_URL + relative
            return full_url
    return None