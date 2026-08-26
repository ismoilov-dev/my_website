from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('blogs/', views.blogs, name='blogs'),
    path('talks/', views.talks, name='talks'),
    path('cv/', views.cv, name='cv'),
    path('feed/', views.feed_list, name='feed'),
    path('feed/<int:pk>/like/', views.feed_like, name='feed_like'),
    path('feed/<int:pk>/comment/', views.feed_comment, name='feed_comment'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
]