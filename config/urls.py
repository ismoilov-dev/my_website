from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.views import healthz

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
    path('ismatismoilov709/', admin.site.urls),
    path('', include('blog.urls')),
]

# In production nginx serves /media/ directly and WhiteNoise serves /static/,
# so Django only needs to hand out uploads while running the dev server.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
