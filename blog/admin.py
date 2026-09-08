"""Admin configuration for everything the public site renders.

The guiding rule here is that a person editing the site should never have to
guess where a record shows up. Every model therefore gets:

* a fieldset ``description`` naming the public page it feeds,
* a changelist that leads with the columns you would actually scan,
* a preview of any uploaded image or file, so a wrong upload is obvious.
"""

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Blog,
    Certificate,
    Education,
    FeedComment,
    FeedPost,
    Project,
    Skill,
    SkillGroup,
    Talk,
    VoluntaryActivity,
    WorkExperience,
)

# CV entries are short prose; the stock 10-row textarea is more box than they
# need and pushes the Save button off screen.
COMPACT_TEXTAREA = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 5})}}

# A blog post is written in this box, so it gets room to write in.
ARTICLE_TEXTAREA = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 22})}}
FEED_TEXTAREA = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 8})}}

ORDER_HELP = (
    'Lowest number appears first on the public page. '
    'Leave every row at 0 to fall back to newest-first.'
)


def _thumb(url, size=42, radius=8):
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;'
        'border-radius:{}px;border:1px solid #d8d8dd;background:#f4f4f5;">',
        url, size, size, radius,
    )


def _dash():
    return mark_safe('<span style="color:#a1a1aa;">—</span>')


class OrderedContentAdmin(admin.ModelAdmin):
    """Shared behaviour for the CV sections, which are hand-ordered lists."""

    formfield_overrides = COMPACT_TEXTAREA
    list_per_page = 50
    save_on_top = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'order' in form.base_fields:
            form.base_fields['order'].help_text = ORDER_HELP
        return form


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    formfield_overrides = ARTICLE_TEXTAREA
    list_display = ('title', 'cover', 'created_at', 'length', 'view_on_site_link')
    list_display_links = ('title',)
    list_filter = ('created_at',)
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('cover_preview', 'updated_at')
    save_on_top = True
    list_per_page = 25

    fieldsets = (
        ('Article', {
            'description': 'Published straight to <b>/blogs/</b> and given its own page. '
                           'The first ~160 characters become the Google and social preview text.',
            'fields': ('title', 'content'),
        }),
        ('Cover image', {
            'description': 'Optional. Shown as a thumbnail in the blog list, '
                           'full width on the article page, and as the social share image.',
            'fields': ('image', 'cover_preview'),
        }),
        ('Publishing', {
            'description': 'Posts are sorted newest first by this date. '
                           'Back-date or future-date a post by changing it.',
            'fields': ('created_at', 'updated_at'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'description': 'Filled in automatically the first time a post is saved. '
                           'Only set this by hand if you want a custom label such as "Last week".',
            'fields': ('time',),
        }),
    )

    @admin.display(description='Cover')
    def cover(self, obj):
        return _thumb(obj.image.url) if obj.image else _dash()

    @admin.display(description='Current cover')
    def cover_preview(self, obj):
        if not obj.image:
            return 'No image uploaded yet.'
        return format_html(
            '<img src="{}" style="max-width:420px;width:100%;border-radius:10px;'
            'border:1px solid #d8d8dd;">', obj.image.url,
        )

    @admin.display(description='Length')
    def length(self, obj):
        return f'{obj.reading_time} min read'

    @admin.display(description='On site')
    def view_on_site_link(self, obj):
        if not obj.pk:
            return _dash()
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Open ↗</a>', obj.get_absolute_url()
        )


class FeedCommentInline(admin.TabularInline):
    """Moderate a post's comments without leaving the post."""

    model = FeedComment
    extra = 0
    fields = ('author_name', 'content', 'created_at', 'is_approved')
    readonly_fields = ('created_at',)
    verbose_name_plural = 'Comments on this post (untick to hide one)'


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    formfield_overrides = FEED_TEXTAREA
    inlines = (FeedCommentInline,)
    list_display = ('summary', 'attachments', 'location', 'likes_count', 'comment_count', 'created_at')
    list_display_links = ('summary',)
    list_filter = ('created_at', 'location')
    search_fields = ('title', 'content', 'location')
    date_hierarchy = 'created_at'
    readonly_fields = ('image_preview', 'likes_count', 'updated_at')
    save_on_top = True
    list_per_page = 25

    fieldsets = (
        ('Post', {
            'description': 'A short update on <b>/feed/</b>. The title is optional — '
                           'leave it empty for a plain note.',
            'fields': ('title', 'content'),
        }),
        ('Media', {
            'description': 'Optional. Attach a photo, a video, or both.',
            'fields': ('image', 'image_preview', 'video'),
        }),
        ('Context', {
            'description': 'Small details shown next to your name on the post.',
            'fields': ('location', 'mood_emoji'),
        }),
        ('Publishing', {
            'description': 'Likes are counted from visitor clicks and cannot be edited here.',
            'fields': ('created_at', 'likes_count', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments')

    @admin.display(description='Post')
    def summary(self, obj):
        if obj.title:
            return obj.title
        if obj.content:
            return obj.content[:60] + ('…' if len(obj.content) > 60 else '')
        return f'Post #{obj.pk}'

    # Not named `media`: that is a ModelAdmin property Django uses for form assets.
    @admin.display(description='Media')
    def attachments(self, obj):
        parts = []
        if obj.image:
            parts.append('🖼 Photo')
        if obj.video:
            parts.append('🎬 Video')
        return ' · '.join(parts) if parts else _dash()

    @admin.display(description='Comments')
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description='Current photo')
    def image_preview(self, obj):
        if not obj.image:
            return 'No photo uploaded yet.'
        return format_html(
            '<img src="{}" style="max-width:320px;width:100%;border-radius:10px;'
            'border:1px solid #d8d8dd;">', obj.image.url,
        )


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    formfield_overrides = COMPACT_TEXTAREA
    list_display = ('author_name', 'preview', 'post', 'created_at', 'is_approved')
    list_display_links = ('author_name',)
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author_name', 'content')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('post',)
    actions = ('approve_comments', 'hide_comments')
    list_per_page = 50

    fieldsets = (
        ('Comment', {
            'description': 'Left by visitors on <b>/feed/</b>. '
                           'Unticking <b>Is approved</b> hides it from the site immediately.',
            'fields': ('post', 'author_name', 'content', 'is_approved', 'created_at'),
        }),
    )

    @admin.display(description='Comment')
    def preview(self, obj):
        return f'{obj.content[:80]}…' if len(obj.content) > 80 else obj.content

    @admin.action(description='Show selected comments on the site')
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comment(s) are now visible.', messages.SUCCESS)

    @admin.action(description='Hide selected comments from the site')
    def hide_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comment(s) are now hidden.', messages.WARNING)


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    formfield_overrides = COMPACT_TEXTAREA
    list_display = ('title', 'has_video', 'created_at')
    list_display_links = ('title',)
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('video_preview', 'updated_at')
    save_on_top = True

    fieldsets = (
        ('Talk', {
            'description': 'Listed on <b>/talks/</b>, newest first.',
            'fields': ('title', 'description'),
        }),
        ('Recording', {
            'description': 'MP4 plays in every browser; MOV, AVI and MKV may not. '
                           'Convert to MP4 if visitors report a blank player.',
            'fields': ('video', 'video_preview'),
        }),
        ('Publishing', {'fields': ('created_at', 'updated_at')}),
    )

    @admin.display(description='Video', boolean=True)
    def has_video(self, obj):
        return bool(obj.video)

    @admin.display(description='Preview')
    def video_preview(self, obj):
        if not obj.video:
            return 'No video uploaded yet.'
        return format_html(
            '<video controls preload="metadata" style="max-width:480px;width:100%;'
            'border-radius:10px;background:#000;"><source src="{}"></video>', obj.video.url,
        )


@admin.register(WorkExperience)
class WorkExperienceAdmin(OrderedContentAdmin):
    list_display = ('title', 'company', 'period', 'order')
    list_display_links = ('title',)
    list_editable = ('order',)
    search_fields = ('title', 'company', 'description')

    fieldsets = (
        ('Role', {
            'description': 'The <b>Work Experience</b> section of <b>/cv/</b>.',
            'fields': ('title', 'company', 'period'),
        }),
        ('Details', {
            'description': 'Start a line with <code>-</code>, <code>*</code> or <code>•</code> '
                           'to render it as a bullet. Wrap text in <code>**stars**</code> for bold.',
            'fields': ('description',),
        }),
        ('Position on the page', {'fields': ('order',)}),
    )


@admin.register(Project)
class ProjectAdmin(OrderedContentAdmin):
    list_display = ('title', 'period', 'link', 'order')
    list_display_links = ('title',)
    list_editable = ('order',)
    search_fields = ('title', 'description')

    fieldsets = (
        ('Project', {
            'description': 'The <b>Projects</b> section of <b>/cv/</b>.',
            'fields': ('title', 'period', 'link'),
        }),
        ('Details', {
            'description': 'Start a line with <code>-</code>, <code>*</code> or <code>•</code> '
                           'to render it as a bullet.',
            'fields': ('description',),
        }),
        ('Position on the page', {'fields': ('order',)}),
    )


@admin.register(Education)
class EducationAdmin(OrderedContentAdmin):
    list_display = ('institution', 'degree', 'period', 'order')
    list_display_links = ('institution',)
    list_editable = ('order',)
    search_fields = ('degree', 'institution')

    fieldsets = (
        ('Study', {
            'description': 'The <b>Education</b> section of <b>/cv/</b>.',
            'fields': ('institution', 'degree', 'period'),
        }),
        ('Details', {'fields': ('description',)}),
        ('Position on the page', {'fields': ('order',)}),
    )


@admin.register(Certificate)
class CertificateAdmin(OrderedContentAdmin):
    list_display = ('title', 'issuer', 'date', 'attachment', 'order')
    list_display_links = ('title',)
    list_editable = ('order',)
    search_fields = ('title', 'issuer', 'description')
    readonly_fields = ('attachment',)

    fieldsets = (
        ('Certificate', {
            'description': 'The <b>Certificates</b> section of <b>/cv/</b>.',
            'fields': ('title', 'issuer', 'date'),
        }),
        ('Proof', {
            'description': 'Upload a file <i>or</i> paste a link. '
                           'If both are given the uploaded file wins.',
            'fields': ('file', 'link', 'attachment'),
        }),
        ('Details', {'fields': ('description',)}),
        ('Position on the page', {'fields': ('order',)}),
    )

    @admin.display(description='Proof')
    def attachment(self, obj):
        target = obj.file.url if obj.file else obj.link
        if not target:
            return _dash()
        return format_html('<a href="{}" target="_blank" rel="noopener">Open ↗</a>', target)


@admin.register(VoluntaryActivity)
class VoluntaryActivityAdmin(OrderedContentAdmin):
    list_display = ('__str__', 'order')
    list_display_links = ('__str__',)
    list_editable = ('order',)
    search_fields = ('title', 'description')

    fieldsets = (
        ('Activity', {
            'description': 'The <b>Voluntary Activities</b> section of <b>/cv/</b>. '
                           'The title is optional.',
            'fields': ('title', 'description'),
        }),
        ('Position on the page', {'fields': ('order',)}),
    )


class SkillInline(admin.TabularInline):
    """Skills are only ever meaningful inside a group, so they are edited there."""

    model = Skill
    extra = 3
    fields = ('name', 'level', 'is_core', 'order')
    ordering = ('order', 'id')


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline', 'skill_count', 'order')
    list_display_links = ('name',)
    list_editable = ('order',)
    search_fields = ('name', 'tagline', 'skills__name')
    inlines = (SkillInline,)
    save_on_top = True

    fieldsets = (
        ('Group', {
            'description': 'One heading in the <b>Skills</b> list, which is the '
                           '<b>/skills/</b> page and the Skills section of '
                           '<b>/cv/</b>. Add the technologies themselves in '
                           'the table below.',
            'fields': ('name', 'tagline'),
        }),
        ('Position in the list', {
            'description': 'Lowest number comes first. The groups flow down '
                           'the left column and continue in the right one.',
            'fields': ('order',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _skill_count=models.Count('skills')
        )

    @admin.display(description='Skills', ordering='_skill_count')
    def skill_count(self, obj):
        return obj._skill_count


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """A flat view of every skill, for when you want to retune levels at once."""

    list_display = ('name', 'group', 'level', 'is_core', 'order')
    list_display_links = ('name',)
    list_editable = ('level', 'is_core', 'order')
    list_filter = ('group', 'level', 'is_core')
    search_fields = ('name',)
    list_per_page = 100

    fieldsets = (
        ('Skill', {
            'description': 'One row in the <b>Skills</b> list, shown on '
                           '<b>/skills/</b> and on <b>/cv/</b>.',
            'fields': ('group', 'name', 'level', 'is_core'),
        }),
        ('Position in the group', {'fields': ('order',)}),
    )
