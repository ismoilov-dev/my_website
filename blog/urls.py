from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('blogs', views.blogs, name='blogs'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
]