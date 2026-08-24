from django.db import models
from django.utils import timezone


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    time = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.time:
            now = timezone.now()
            diff = now - self.created_at
            
            if diff.total_seconds() < 60:
                self.time = "Just now"
            elif diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() // 60)
                self.time = f"{minutes} min ago"
            elif diff.total_seconds() < 86400:
                hours = int(diff.total_seconds() // 3600)
                self.time = f"{hours} hours ago"
            else:
                days = int(diff.total_seconds() // 86400)
                if days == 1:
                    self.time = "1 day ago"
                else:
                    self.time = f"{days} days ago"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title