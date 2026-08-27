from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import (
    Blog,
    Certificate,
    Education,
    FeedComment,
    FeedPost,
    Project,
    VoluntaryActivity,
    WorkExperience,
)


def index(request):
    return render(request, 'blog.html')


def about(request):
    return render(request, 'about.html')


def blogs(request):
    return render(request, 'blogs.html', {'blogs': Blog.objects.all()})


def talks(request):
    return render(request, 'talks.html')


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    # Neighbours in publication order, so a reader can move through the archive.
    previous_post = Blog.objects.filter(created_at__lt=blog.created_at).first()
    next_post = Blog.objects.filter(created_at__gt=blog.created_at).last()

    return render(request, 'blog_detail.html', {
        'blog': blog,
        'previous_post': previous_post,
        'next_post': next_post,
    })


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


def feed_list(request):
    posts = FeedPost.objects.prefetch_related('comments').all()
    liked_post_ids = request.session.get('liked_feed_posts', [])
    return render(request, 'feed.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids
    })


@require_POST
def feed_like(request, pk):
    post = get_object_or_404(FeedPost, pk=pk)
    liked_posts = request.session.get('liked_feed_posts', [])
    
    if pk in liked_posts:
        # Unlike
        if post.likes_count > 0:
            post.likes_count -= 1
            post.save()
        liked_posts.remove(pk)
        request.session['liked_feed_posts'] = liked_posts
        is_liked = False
    else:
        # Like
        post.likes_count += 1
        post.save()
        liked_posts.append(pk)
        request.session['liked_feed_posts'] = liked_posts
        is_liked = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'ok', 'likes_count': post.likes_count, 'liked': is_liked})
    return redirect('feed')


@require_POST
def feed_comment(request, pk):
    post = get_object_or_404(FeedPost, pk=pk)
    author_name = request.POST.get('author_name', '').strip() or 'Anonymous Reader'
    content = request.POST.get('content', '').strip()
    
    if content:
        comment = FeedComment.objects.create(
            post=post,
            author_name=author_name,
            content=content
        )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'ok',
                'author_name': comment.author_name,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
            })
            
    return redirect('feed')