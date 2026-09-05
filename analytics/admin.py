from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.template.response import TemplateResponse
from django.utils import timezone

from .models import PageView, UniqueVisitor, VisitorLog


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('path', 'ip_address')
    date_hierarchy = 'timestamp'
    readonly_fields = ('path', 'timestamp', 'ip_address')

    def has_add_permission(self, request):
        return False


@admin.register(UniqueVisitor)
class UniqueVisitorAdmin(admin.ModelAdmin):
    list_display = ('date', 'ip_address')
    list_filter = ('date',)
    search_fields = ('ip_address',)
    date_hierarchy = 'date'
    readonly_fields = ('date', 'ip_address')

    def has_add_permission(self, request):
        return False


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'path', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('session_id', 'path', 'ip_address')
    readonly_fields = ('session_id', 'path', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False


def analytics_dashboard(request, extra_context=None):
    """Replace the admin home with a compact, useful traffic overview."""
    today = timezone.localdate()
    seven_days_ago = today - timezone.timedelta(days=6)
    daily_counts = {
        row['date']: row['visitors']
        for row in UniqueVisitor.objects.filter(date__gte=seven_days_ago)
        .values('date').annotate(visitors=Count('id'))
    }
    daily_visitors = [
        {'date': seven_days_ago + timezone.timedelta(days=offset),
         'visitors': daily_counts.get(seven_days_ago + timezone.timedelta(days=offset), 0)}
        for offset in range(7)
    ]
    today_start = timezone.make_aware(
        timezone.datetime.combine(today, timezone.datetime.min.time())
    )
    context = {
        **admin.site.each_context(request),
        'title': 'Site analytics',
        'subtitle': None,
        'app_list': admin.site.get_app_list(request),
        'today': today,
        'today_unique_visitors': daily_counts.get(today, 0),
        'today_page_views': PageView.objects.filter(timestamp__gte=today_start).count(),
        'seven_day_unique_visitors': sum(day['visitors'] for day in daily_visitors),
        'daily_visitors': daily_visitors,
        'top_pages': PageView.objects.filter(timestamp__gte=today_start)
        .values('path').annotate(views=Count('id')).order_by('-views', 'path')[:5],
        **(extra_context or {}),
    }
    return TemplateResponse(request, 'analytics/admin/dashboard.html', context)


admin.site.index = analytics_dashboard
