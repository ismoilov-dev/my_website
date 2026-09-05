from django.db import models

class VisitorLog(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_id} - {self.path}"


class PageView(models.Model):
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

class UniqueVisitor(models.Model):
    ip_address = models.GenericIPAddressField()
    date = models.DateField(auto_now_add=True)

