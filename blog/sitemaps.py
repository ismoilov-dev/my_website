from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Blog


class StaticViewSitemap(Sitemap):
    """The hand-written pages: home, about, blog index, talks, CV, feed."""

    changefreq = 'weekly'

    def items(self):
        return ['index', 'about', 'blogs', 'talks', 'cv', 'feed']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        # The homepage is what should rank for a search on the name, so it
        # carries more weight than the section pages.
        return 1.0 if item == 'index' else 0.8


class BlogSitemap(Sitemap):
    """Individual posts, newest first, with a real last-modified date."""

    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Blog.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}
