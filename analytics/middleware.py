import ipaddress

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from .models import PageView, UniqueVisitor


class TrackVisitorMiddleware:
    """Record successful requests for public HTML pages only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self.should_track(request, response):
            ip_address = self.get_client_ip(request)
            PageView.objects.create(path=request.path[:255], ip_address=ip_address)

            # A missing/invalid address cannot identify a unique person. It is
            # still kept as a page view so totals remain useful.
            if ip_address:
                try:
                    UniqueVisitor.objects.get_or_create(
                        ip_address=ip_address, date=timezone.localdate(),
                    )
                except IntegrityError:
                    # Two simultaneous first requests can both try to create
                    # the same daily visitor; the database constraint wins.
                    pass
        return response

    def should_track(self, request, response):
        admin_prefix = f'/{settings.ADMIN_URL.lstrip("/")}'
        ignored_prefixes = (admin_prefix, settings.STATIC_URL, settings.MEDIA_URL)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        bot_markers = ('bot', 'crawler', 'spider', 'slurp', 'facebookexternalhit')

        return (
            request.method == 'GET'
            and response.status_code < 400
            and not request.path.startswith(ignored_prefixes)
            and not any(marker in user_agent.lower() for marker in bot_markers)
        )

    def get_client_ip(self, request):
        candidate = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        candidate = candidate or request.META.get('REMOTE_ADDR', '')
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            return None
