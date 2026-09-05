# middleware.py
from django.utils import timezone
from .models import PageView, UniqueVisitor

class TrackVisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tracking for admin or static paths if desired
        if not request.path.startswith('/admin/'):
            ip = self.get_client_ip(request)
            today = timezone.now().date()

            # Always count the raw pageview/hit
            PageView.objects.create(path=request.path, ip_address=ip)

            # Count unique visitor once per day per IP
            UniqueVisitor.objects.get_or_create(ip_address=ip, date=today)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
