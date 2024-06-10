from django.db import models
from uuid import uuid4
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def validate_future_date(value):
    if value > date.today(): 
        raise ValidationError('Дата не может быть в прошлом')


def validate_difficulty_range(value):
    if value < 0 or value > 5:
        raise ValidationError('Сложность должна быть от 0 до 5 включительно', params={'value': value})


def max_length(value):
    if len(value) > 100:
        raise ValidationError('Значение не может превышать 100 символов', params={'value': value})

class UserMixin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Task(UUIDMixin, UserMixin):
    name = models.TextField(validators=[max_length])
    description = models.TextField()
    difficulty = models.IntegerField(validators=[validate_difficulty_range], default=0)

    students = models.ManyToManyField("Student", through='TaskStudent')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"


class Student(UUIDMixin, UserMixin):
    nickname = models.TextField(validators=[max_length])
    registration_date = models.DateField(validators=[validate_future_date], default=date.today, editable=False)

    tasks = models.ManyToManyField(Task, through='TaskStudent')

    def __str__(self):
        return self.nickname

    class Meta:
        ordering = ['registration_date']
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def rating(self):
        return round(sum([task.difficulty for task in self.tasks.all()]) / len(self.tasks.all()), 2) if len (self.tasks.all()) > 0 else 0

class TaskStudent(UUIDMixin):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    solution = models.TextField()

    class Meta:
        ordering = ['task']
        verbose_name = "TaskStudent"
        verbose_name_plural = "TaskStudents"
        unique_together = ('task', 'student')


class Comment(UUIDMixin):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_comments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='related_comments')
    text_comment = models.TextField()
    date_publication = models.DateField(default=date.today, validators=[validate_future_date], editable=False)

    def __str__(self):
        return f'Comment by {self.task_id.name} at {self.date_publication}'

    class Meta:
        ordering = ['date_publication']
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
