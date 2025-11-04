from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from wagtail.images.views.serve import ServeView
from webpush.views import save_info

from home.views import get_manifest, LogoutRedirectHackView
from iogt_users import urls as users_urls
from search import views as search_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from home import views as pwa_views
from wagtail_transfer import urls as wagtailtransfer_urls
from admin_login import urls as admin_login_urls
from admin_login.views import AzureADSignupView
from iogt.views import (
    TransitionPageView,
    SitemapAPIView,
    TranslationNotFoundPage,
    PageTreeAPIView,
    OfflineContentNotFoundPageView,
    CustomLogoutView,
)
from iogt import pwa_views
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

api_url_patterns = [
    path('api/v1/questionnaires/', include('questionnaires.api.v1.urls')),
    path('api/interactive/', include('interactive.api.urls')),
    # path("notifications/save-preference/", save_notification_preference, name="save_notification_preference"),
    
]

schema_view = get_schema_view(
    openapi.Info(
        title="IoGT API",
        default_version='v1',
        description="IoGT APIs",
    ),
    url=settings.WAGTAILADMIN_BASE_URL,
    public=True,
    patterns=api_url_patterns
)

urlpatterns = api_url_patterns + [
    path('django-admin/', admin.site.urls),
    path('admin/logout/', CustomLogoutView.as_view(), name='admin_logout'),
    path('admin/login/', AzureADSignupView.as_view(), name='azure_signup_view'),  # Override Wagtail admin login
    re_path(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('admin-login/', include(admin_login_urls), name='admin_login_urls'),
    *i18n_patterns(path('logout_hack_view', LogoutRedirectHackView.as_view(), name='logout_redirect')),
    *i18n_patterns(path('search/', search_views.search, name='search')),
    *i18n_patterns(path('users/', include(users_urls), name='users_urls')),
    *i18n_patterns(path('accounts/', include('allauth.urls'), name='allauth-urls')),
    *i18n_patterns(path('comments/', include('django_comments_xtd.urls'))),
    path(
        'sw.js',
        pwa_views.ServiceWorkerView.as_view(),
        name=pwa_views.ServiceWorkerView.name,
    ),
    *i18n_patterns(path("external-link/", TransitionPageView.as_view(), name="external-link")),
    *i18n_patterns(path("translation-not-found/", TranslationNotFoundPage.as_view(), name="translation-not-found")),
    *i18n_patterns(path("offline-content-not-found/", OfflineContentNotFoundPageView.as_view(), name="offline_content_not_found")),

    path('messaging/', include('messaging.urls'), name='messaging-urls'),
    path('home/', include('home.urls'), name='home-urls'),
    path('wagtail-transfer/', include(wagtailtransfer_urls)),
    path('sitemap/', SitemapAPIView.as_view(), name='sitemap'),
    path("manifest.webmanifest", get_manifest, name="manifest"),
    *i18n_patterns(path('comments/', include('comments.urls'))),
    *i18n_patterns(path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')),
    path('health-check/', include('health_check.urls')),
    path('page-tree/<int:page_id>/', PageTreeAPIView.as_view(), name='page_tree'),
    path('api/docs/', schema_view.with_ui('swagger'), name='swagger'),
    path('webpush/subscribe/', save_info, name='save_webpush_info'),
    path('inbox/notifications/', include('notifications.urls', namespace='notifications')),
    path('notifications/', include('user_notifications.urls')),
    path("manifest.webmanifest", pwa_views.manifest, name="manifest"),
    path("sw.js", pwa_views.service_worker, name="sw.js"),
]

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # add django debug toolbar links
    urlpatterns = urlpatterns + [path(r"__debug__/", include(debug_toolbar.urls))]

urlpatterns = urlpatterns + i18n_patterns(
    re_path(r'^images/([^/]*)/(\d*)/([^/]*)/[^/]*$', ServeView.as_view(), name='wagtailimages_serve'),
    path("", include(wagtail_urls)),
)
