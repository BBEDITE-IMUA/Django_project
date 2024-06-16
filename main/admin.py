"""
This module contains the admin interface configurations for the Task, Student, TaskStudent, and Comment models.

Each model has a corresponding admin class that extends admin.ModelAdmin and is decorated with @admin.register.

Administrator classes define list-based fields (list_display) and read-only fields (readonly_fields).
"""

from django.contrib import admin

from .models import Comment, Student, Task, TaskStudent

ID_FIELD = 'id'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Task admin configuration."""

    list_display = ('name', 'description', 'difficulty')
    readonly_fields = (ID_FIELD,)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin configuration."""

    list_display = ('nickname', 'registration_date', 'rating')
    readonly_fields = (ID_FIELD,)


@admin.register(TaskStudent)
class TaskStudentAdmin(admin.ModelAdmin):
    """TaskStudent admin configuration."""

    list_display = ('task', 'student', 'solution')
    readonly_fields = (ID_FIELD,)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin configuration."""

    list_display = ('task_id', 'student', 'text_comment', 'date_publication')
    readonly_fields = (ID_FIELD,)
