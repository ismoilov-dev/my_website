from django.contrib.admin.apps import AdminConfig


class PortfolioAdminConfig(AdminConfig):
    """Mounts PortfolioAdminSite as the project's one and only admin site."""

    default_site = 'config.admin_site.PortfolioAdminSite'
