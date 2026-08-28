from django.contrib import admin

from .models import (
    Blog,
    Certificate,
    Education,
    FeedComment,
    FeedPost,
    Project,
    Talk,
    WorkExperience,
)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'time', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'period', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'company', 'description')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'link', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'period', 'order')
    list_editable = ('order',)
    search_fields = ('degree', 'institution')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'date', 'file', 'link', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'issuer', 'description')


class FeedCommentInline(admin.TabularInline):
    model = FeedComment
    extra = 0
    fields = ('author_name', 'content', 'created_at', 'is_approved')
    readonly_fields = ('created_at',)


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'mood_emoji', 'location', 'likes_count', 'created_at')
    list_filter = ('created_at', 'location')
    search_fields = ('title', 'content', 'location')
    inlines = [FeedCommentInline]


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author_name', 'content', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author_name', 'content')


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'video', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)




