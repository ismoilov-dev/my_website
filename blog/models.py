from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True, help_text="Optional blog cover image")
    time = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.pk])

    @property
    def excerpt(self):
        """Short plain-text preview used in listings and meta descriptions."""
        return Truncator(strip_tags(self.content)).chars(160)

    @property
    def reading_time(self):
        """Estimated reading time in whole minutes (200 words per minute)."""
        words = len(strip_tags(self.content).split())
        return max(1, round(words / 200))


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


class FeedPost(models.Model):
    title = models.CharField(max_length=250, blank=True, null=True, help_text="Optional post title")
    content = models.TextField(help_text="Share a story, thought or life update")
    image = models.FileField(upload_to='feed/', blank=True, null=True, help_text="Optional photo/image for the post")
    location = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Tashkent, Uzbekistan")
    mood_emoji = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. ☕, 💻, 🚀, 🏔️")
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feed Post"
        verbose_name_plural = "Feed Posts"

    def __str__(self):
        return self.title or f"Feed Post #{self.id} - {self.created_at.strftime('%Y-%m-%d')}"


class FeedComment(models.Model):
    post = models.ForeignKey(FeedPost, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100, default="Anonymous Reader")
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Feed Comment"
        verbose_name_plural = "Feed Comments"

    def __str__(self):
        return f"Comment by {self.author_name} on Post #{self.post.id}"


class Talk(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    video = models.FileField(
        upload_to='talks/videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm'])],
        verbose_name="Video fayl",
        help_text="MP4, MOV, AVI, MKV yoki WEBM formatidagi videolarni yuklang"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Talk"
        verbose_name_plural = "Talks"

    def __str__(self):
        return self.title