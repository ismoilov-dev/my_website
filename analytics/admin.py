"""Read-only admin views over the traffic tables.

Nothing here is editable: the rows are written by the tracking middleware, and
letting them be hand-edited would only make the dashboard lie. The dashboard
itself lives on the admin site (config/admin_site.py) because it also reports on
blog content, not just traffic.
"""

from django.contrib import admin

from .models import PageView, UniqueVisitor, VisitorLog


class ReadOnlyAdmin(admin.ModelAdmin):
    """Browsable history: search and filter, but no adding, editing or deleting."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageView)
class PageViewAdmin(ReadOnlyAdmin):
    list_display = ('path', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('path', 'ip_address')
    date_hierarchy = 'timestamp'
    list_per_page = 50


@admin.register(UniqueVisitor)
class UniqueVisitorAdmin(ReadOnlyAdmin):
    list_display = ('date', 'ip_address')
    list_filter = ('date',)
    search_fields = ('ip_address',)
    date_hierarchy = 'date'
    list_per_page = 50


@admin.register(VisitorLog)
class VisitorLogAdmin(ReadOnlyAdmin):
    list_display = ('timestamp', 'path', 'ip_address', 'session_id')
    list_filter = ('timestamp',)
    search_fields = ('session_id', 'path', 'ip_address')
    date_hierarchy = 'timestamp'
    list_per_page = 50
