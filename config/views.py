import logging

from django.db import connection
from django.http import JsonResponse

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
