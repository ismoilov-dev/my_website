from django.contrib import admin
from .models import Blog, WorkExperience, Project, Education, VoluntaryActivity, Certificate

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


