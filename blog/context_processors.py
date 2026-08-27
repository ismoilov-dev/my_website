from django.conf import settings


def site_identity(request):
    """Expose the site's public identity to every template.

    The footer, the meta tags and the structured data all describe the same
    person, so they read from one place rather than repeating the links.
    """
    return {
        'site_author': settings.SITE_AUTHOR,
        'site_job_title': settings.SITE_JOB_TITLE,
        'social_profiles': settings.SOCIAL_PROFILES,
        'google_site_verification': settings.GOOGLE_SITE_VERIFICATION,
    }
