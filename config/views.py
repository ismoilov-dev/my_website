import logging

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

logger = logging.getLogger(__name__)


def healthz(request):
    """
    Health check endpoint for container orchestrators and monitoring tools.
    Checks database connection and system status.
    """
    try:
        connection.ensure_connection()
        if not connection.is_usable():
            return JsonResponse({"status": "error", "database": "unusable"}, status=500)
    except Exception as e:
        logger.error(f"Healthcheck database check failed: {e}")
        return JsonResponse({"status": "error", "database": "unavailable", "detail": str(e)}, status=500)

    return JsonResponse({"status": "ok", "database": "ok"})


def robots_txt(request):
    """Crawler instructions, served from the site root.

    Everything public is open to indexing. The admin and the health check are
    excluded: neither belongs in search results, and the admin path is not
    something to advertise. The sitemap line is how a crawler that arrives
    without a link discovers every page in one request.
    """
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Disallow: {reverse("admin:index")}',
        f'Disallow: {reverse("healthz")}',
        '',
        f'Sitemap: {request.build_absolute_uri(reverse("django.contrib.sitemaps.views.sitemap"))}',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


def google_verification_file(request):
    """Serve the ownership token file Google Search Console fetches.

    The body is the single line Google expects: the literal filename it asked
    for, prefixed with google-site-verification.
    """
    return HttpResponse(
        f'google-site-verification: {settings.GOOGLE_SITE_VERIFICATION_FILE}\n',
        content_type='text/html',
    )
