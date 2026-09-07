from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(
        upload_to='blog/', blank=True, null=True,
        help_text='Landscape images work best. Around 1200x630 pixels is ideal.',
    )
    time = models.CharField(
        max_length=50, blank=True, null=True,
        help_text='Set automatically on first save, e.g. "3 days ago".',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog post'
        verbose_name_plural = 'Blog posts'

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
    period = models.CharField(max_length=100, help_text='e.g. "Jan 2024 — Present"')
    description = models.TextField(
        blank=True,
        help_text='One duty or achievement per line. Start a line with "-" for a bullet.',
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Work experience'
        verbose_name_plural = 'Work experience'

    def __str__(self):
        return f"{self.title} at {self.company}"


class Project(models.Model):
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=100, blank=True, null=True, help_text='e.g. "2024"')
    description = models.TextField(
        help_text='One point per line. Start a line with "-" for a bullet.',
    )
    link = models.URLField(blank=True, null=True, help_text='GitHub, demo or live URL.')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return self.title


class Education(models.Model):
    institution = models.CharField(max_length=200, help_text='School or university name.')
    degree = models.CharField(max_length=200, help_text='e.g. "BSc Computer Science"')
    period = models.CharField(max_length=100, help_text='e.g. "2020 — 2024"')
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Education entry'
        verbose_name_plural = 'Education'

    def __str__(self):
        return f"{self.degree} - {self.institution}"



class VoluntaryActivity(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Voluntary activity'
        verbose_name_plural = 'Voluntary activities'

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
    video = models.FileField(
        upload_to='feed/videos/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm'])],
        help_text="Optional video for the post (MP4, MOV, AVI, MKV, WEBM)"
    )
    location = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Tashkent, Uzbekistan")
    mood_emoji = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. ☕, 💻, 🚀, 🏔️")
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Feed post'
        verbose_name_plural = 'Feed posts'

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
        verbose_name = 'Feed comment'
        verbose_name_plural = 'Feed comments'

    def __str__(self):
        return f"Comment by {self.author_name} on Post #{self.post.id}"


class Talk(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video = models.FileField(
        upload_to='talks/videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm'])],
        help_text='MP4 plays everywhere. MOV, AVI, MKV and WEBM are accepted '
                  'but may not play in every browser.'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Talk'
        verbose_name_plural = 'Talks'

    def __str__(self):
        return self.title

class SkillGroup(models.Model):
    """One cluster of related skills — a single heading in the /cv/ list."""

    name = models.CharField(max_length=80, help_text='e.g. "Backend", "Data", "DevOps".')
    tagline = models.CharField(
        max_length=120, blank=True,
        help_text='Optional one-liner shown next to the group name.',
    )
    order = models.IntegerField(
        default=0,
        help_text='Lowest number comes first in the list.',
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Skill group'
        verbose_name_plural = 'Skill groups'

    def __str__(self):
        return self.name


class Skill(models.Model):
    """A single technology, listed under its group on the CV."""

    LEVELS = (
        (1, 'Learning'),
        (2, 'Working knowledge'),
        (3, 'Comfortable'),
        (4, 'Strong'),
        (5, 'Core strength'),
    )

    group = models.ForeignKey(SkillGroup, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=80)
    level = models.PositiveSmallIntegerField(
        choices=LEVELS, default=3,
        help_text='Sets how far the level bar is filled on the CV.',
    )
    years = models.CharField(
        max_length=20, blank=True,
        help_text='Optional, e.g. "4y". Shown next to the skill.',
    )
    is_core = models.BooleanField(
        'Highlight', default=False,
        help_text='Marks the skill CORE on the CV, for the few you lead with.',
    )
    order = models.IntegerField(default=0)

    class Meta:
        # Insertion order, not the reverse of it: these are typed as inline
        # rows under their group, so what you see while editing is what ships.
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    @property
    def percent(self):
        """The level as a share of the scale, for the width of its bar."""
        return round(self.level / len(self.LEVELS) * 100)
