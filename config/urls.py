from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('ismatismoilov709/', admin.site.urls),
    path('', include('blog.urls')),
]
