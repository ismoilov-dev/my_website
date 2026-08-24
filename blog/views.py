from django.shortcuts import render, get_object_or_404
from .models import Blog, WorkExperience, Project, Education, VoluntaryActivity, Certificate

def index(request):
    return render(request, 'blog.html')


def about(request):
    return render(request, 'about.html')


def blogs(request):
    blogs_list = Blog.objects.all().order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs_list})


def talks(request):
    return render(request, 'talks.html')


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog_detail.html', {'blog': blog})


def cv(request):
    experiences = WorkExperience.objects.all().order_by('order', '-id')
    projects = Project.objects.all().order_by('order', '-id')
    educations = Education.objects.all().order_by('order', '-id')
    activities = VoluntaryActivity.objects.all().order_by('order', '-id')
    certificates = Certificate.objects.all().order_by('order', '-id')
    
    return render(request, 'cv.html', {
        'experiences': experiences,
        'projects': projects,
        'educations': educations,
        'activities': activities,
        'certificates': certificates,
    })