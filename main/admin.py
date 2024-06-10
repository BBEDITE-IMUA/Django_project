from django.contrib import admin
from .models import Task, Student, TaskStudent, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'difficulty')
    readonly_fields = ('id',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'registration_date', 'rating')
    readonly_fields = ('id',)


@admin.register(TaskStudent)
class TaskStudentAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'solution')
    readonly_fields = ('id',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'student', 'text_comment', 'date_publication')
    readonly_fields = ('id',)
