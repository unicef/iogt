from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from home.views import get_manifest, LogoutRedirectHackView
from iogt_users import urls as users_urls
from search import views as search_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from home import views as pwa_views
from wagtail_transfer import urls as wagtailtransfer_urls
from iogt.views import TransitionPageView, SitemapAPIView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
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
    *i18n_patterns(path('messaging/', include('messaging.urls'), name='messaging-urls')),
    path('wagtail-transfer/', include(wagtailtransfer_urls)),
    path('sitemap/', SitemapAPIView.as_view(), name='sitemap'),
    path("manifest.webmanifest", get_manifest, name="manifest"),
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
    path("", include(wagtail_urls)),
)
