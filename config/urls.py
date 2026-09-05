from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from blog.sitemaps import sitemaps
from config.views import google_verification_file, healthz, robots_txt

urlpatterns = [
    path('healthz/', healthz, name='healthz'),

    # Search engine entry points, both served from the root where crawlers
    # look for them.
    path('robots.txt', robots_txt, name='robots_txt'),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),

    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('blog.urls')),
]

# Google Search Console ownership check. The route exists only when the exact
# filename is configured; the '/' guard keeps a stray value from mounting
# something other than a single root-level file.
_verification_file = settings.GOOGLE_SITE_VERIFICATION_FILE
if _verification_file and '/' not in _verification_file:
    urlpatterns.insert(
        0,
        path(_verification_file, google_verification_file, name='google_verification'),
    )

# In production nginx serves /media/ directly and WhiteNoise serves /static/,
# so Django only needs to hand out uploads while running the dev server.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
