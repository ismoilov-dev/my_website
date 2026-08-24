from django.shortcuts import render, get_object_or_404
from .models import Blog

def index(request):
    return render(request, 'blog.html')


def about(request):
    return render(request, 'about.html')


def blogs(request):
    blogs_list = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs_list})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog_detail.html', {'blog': blog})