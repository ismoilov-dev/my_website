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


class WorkExperience(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    period = models.CharField(max_length=100)
    description = models.TextField(help_text="Enter bullet points or description of duties/achievements", blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"

    def __str__(self):
        return f"{self.title} at {self.company}"


class Project(models.Model):
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return self.title


class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    period = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return f"{self.degree} - {self.institution}"



class VoluntaryActivity(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name_plural = 'Voluntary Activities'

    def __str__(self):
        return self.title or f"Activity {self.id}"


class Certificate(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Coursera, Udemy, Sfera Academy")
    date = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 2024")
    file = models.FileField(upload_to='certificates/', blank=True, null=True, help_text="Upload certificate file (PDF, PNG, JPG)")
    link = models.URLField(blank=True, null=True, help_text="Certificate URL if available")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return self.title