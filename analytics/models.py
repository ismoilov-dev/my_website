from django.db import models


class VisitorLog(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_id} - {self.path}"


class PageView(models.Model):
    """One successful public-page request."""

    path = models.CharField(max_length=255, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = 'page view'
        verbose_name_plural = 'page views'

    def __str__(self):
        return f'{self.path} at {self.timestamp:%Y-%m-%d %H:%M}'


class UniqueVisitor(models.Model):
    """A single identifiable visitor on a calendar day (site timezone)."""

    ip_address = models.GenericIPAddressField()
    date = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('ip_address', 'date'), name='unique_visitor_per_day',
            ),
        ]
        ordering = ('-date',)
        verbose_name = 'daily unique visitor'
        verbose_name_plural = 'daily unique visitors'

    def __str__(self):
        return f'{self.ip_address} on {self.date:%Y-%m-%d}'
