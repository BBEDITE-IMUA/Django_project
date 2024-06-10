from django import forms
from .models import Task, Comment, Student, TaskStudent

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'difficulty']
        labels = {
            'name': 'Название задачи',
            'description': 'Описание задачи',
            'difficulty': 'Сложность задачи'
        }
        error_messages = {
            'name': {
                'unique': 'Задача с таким названием уже существует.',
                'max_length': 'Название задачи не должно превышать 100 символов.',
                'required': 'Поле обязательно для заполнения.'
            },
            'description': {
                'required': 'Поле обязательно для заполнения.'
            },
            'difficulty': {
                'required': 'Поле обязательно для заполнения.'
            }
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['task_id', 'student', 'text_comment']
        labels = {
            'task_id': 'Задача',
            'student': 'Студент',
            'text_comment': 'Текст комментария'
        }
        error_messages = {
            'task_id': {
                'required': 'Поле обязательно для заполнения.'
            },
            'student': {
                'required': 'Поле обязательно для заполнения.'
            },
            'text_comment': {
                'required': 'Поле обязательно для заполнения.'
            }
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['nickname']
        labels = {
            'nickname': 'Псевдоним'
        }
        error_messages = {
            'nickname': {
                'unique': 'Студент с таким псевдонимом уже существует.',
                'max_length': 'Псевдоним не должен превышать 100 символов.',
                'required': 'Поле обязательно для заполнения.'
            }
        }

class TaskStudentForm(forms.ModelForm):
    class Meta:
        model = TaskStudent
        fields = ['task', 'student', 'solution']
        labels = {
            'task': 'Задача',
            'student': 'Студент',
            'solution': 'Решение'
        }
        error_messages = {
            'task': {
                'required': 'Поле обязательно для заполнения.'
            },
            'student': {
                'required': 'Поле обязательно для заполнения.'
            },
            'solution': {
                'required': 'Поле обязательно для заполнения.'
            }
        }