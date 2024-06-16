"""
This module contains form classes for the Task, Comment, Student, and TaskStudent models.

Each form class extends forms.ModelForm and has a nested Meta class that defines the model and fields for the form.
"""

from django import forms

from .models import Comment, Student, Task, TaskStudent

REQUIRED_FIELD_ERROR = 'Поле обязательно для заполнения.'
STUDENT_FIELD = 'student'
REQUIRED = 'required'


class TaskForm(forms.ModelForm):
    """
    Form for creating and updating Task instances.

    The form uses the Task model and includes the 'name', 'description', and 'difficulty' fields.
    """

    class Meta:
        model = Task
        fields = ['name', 'description', 'difficulty']
        labels = {
            'name': 'Название задачи',
            'description': 'Описание задачи',
            'difficulty': 'Сложность задачи',
        }
        error_messages = {
            'name': {
                'unique': 'Задача с таким названием уже существует.',
                'max_length': 'Название не должно превышать 100 символов.',
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            'description': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            'difficulty': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
        }


class CommentForm(forms.ModelForm):
    """
    Form for creating and updating Comment instances.

    The form uses the Comment model and includes the 'task_id', STUDENT_FIELD, and 'text_comment' fields.
    """

    class Meta:
        model = Comment
        fields = ['task_id', STUDENT_FIELD, 'text_comment']
        labels = {
            'task_id': 'Задача',
            STUDENT_FIELD: 'Студент',
            'text_comment': 'Текст комментария',
        }
        error_messages = {
            'task_id': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            STUDENT_FIELD: {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            'text_comment': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
        }


class StudentForm(forms.ModelForm):
    """
    Form for creating and updating Student instances.

    The form uses the Student model and includes the 'nickname' field.
    """

    class Meta:
        model = Student
        fields = ['nickname']
        labels = {
            'nickname': 'Псевдоним',
        }
        error_messages = {
            'nickname': {
                'unique': 'Студент с таким псевдонимом уже существует.',
                'max_length': 'Псевдоним не должен превышать 100 символов.',
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
        }


class TaskStudentForm(forms.ModelForm):
    """
    Form for creating and updating TaskStudent instances.

    The form uses the TaskStudent model and includes the 'task', STUDENT_FIELD, and 'solution' fields.
    """

    class Meta:
        model = TaskStudent
        fields = ['task', STUDENT_FIELD, 'solution']
        labels = {
            'task': 'Задача',
            STUDENT_FIELD: 'Студент',
            'solution': 'Решение',
        }
        error_messages = {
            'task': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            STUDENT_FIELD: {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
            'solution': {
                REQUIRED: REQUIRED_FIELD_ERROR,
            },
        }
