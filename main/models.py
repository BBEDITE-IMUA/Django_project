"""
This module defines the data models for the application.

It includes models for tasks, students, task-student associations, and comments.
It also includes several utility classes and validation functions.

Each model is a Django model, which means it corresponds to a database table.
The fields on each model represent the columns in the database table,
and each instance of the model represents a row in the table.

The utility classes include mixins for adding a UUID primary key field
and a foreign key to the User model to other models.

The validation functions are used to ensure that the data stored in the models is valid.
They are used as validators on the appropriate model fields.
"""

from datetime import date
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_future_date(date_value):
    """
    Validate that the provided date is not in the past.

    Args:
        date_value (date): The date to validate.

    Raises:
        ValidationError: If the date is in the past.
    """
    if date_value > date.today():
        raise ValidationError('Дата не может быть в прошлом')


def validate_difficulty_range(difficulty_value):
    """
    Validate that the provided difficulty value is within the range 0-5.

    Args:
        difficulty_value (int): The difficulty value to validate.

    Raises:
        ValidationError: If the difficulty value is not within the range 0-5.
    """
    if difficulty_value < 0 or difficulty_value > 5:
        raise ValidationError('Сложность должна быть от 0 до 5 включительно', params={'value': difficulty_value})


def max_length(string_value):
    """
    Validate that the provided string is not longer than 100 characters.

    Args:
        string_value (str): The string to validate.

    Raises:
        ValidationError: If the string is longer than 100 characters.
    """
    if len(string_value) > 100:
        raise ValidationError('Значение не может превышать 100 символов', params={'value': string_value})


class UserMixin(models.Model):
    """Abstract base class that adds a foreign key to the User model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    """Abstract base class that adds a UUID primary key field."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Task(UUIDMixin, UserMixin):
    """
    Model representing a task.

    Each task has a name, description, and difficulty level, and is associated with multiple students.
    """

    name = models.TextField(validators=[max_length])
    description = models.TextField()
    difficulty = models.IntegerField(validators=[validate_difficulty_range], default=0)

    students = models.ManyToManyField('Student', through='TaskStudent')

    def __str__(self):
        """
        Return the name of the task.

        Returns:
            str: The name of the task.
        """
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'


class Student(UUIDMixin, UserMixin):
    """
    Model representing a student.

    Each student has a nickname and registration date, and is associated with multiple tasks.
    """

    nickname = models.TextField(validators=[max_length])
    registration_date = models.DateField(validators=[validate_future_date], default=date.today, editable=False)

    tasks = models.ManyToManyField(Task, through='TaskStudent')

    def __str__(self):
        """
        Return the nickname of the student.

        Returns:
            str: The nickname of the student.
        """
        return self.nickname

    class Meta:
        ordering = ['registration_date']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    @property
    def rating(self):
        """
        Calculate the average difficulty of the tasks associated with the student.

        Returns:
            float: The average difficulty of the tasks, rounded to 2 decimal places.
        """
        summ = [task.difficulty for task in self.tasks.all()]
        len_tasks = len(self.tasks.all())
        return round(sum(summ) / len_tasks, 2) if len_tasks > 0 else 0


class TaskStudent(UUIDMixin):
    """
    Model representing the association between a task and a student.

    Each association has a solution text field.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    solution = models.TextField()

    class Meta:
        ordering = ['task']
        verbose_name = 'TaskStudent'
        verbose_name_plural = 'TaskStudents'
        unique_together = ('task', 'student')


class Comment(UUIDMixin):
    """
    Model representing a comment.

    Each comment is associated with a task and a student, and has a text field and publication date.
    """

    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_comments')

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='related_comments')

    text_comment = models.TextField()
    date_publication = models.DateField(default=date.today, validators=[validate_future_date], editable=False)

    def __str__(self):
        """
        Return a string representation of the comment.

        Returns:
            str: A string representation of the comment.
        """
        return f'Comment by {self.task_id.name} at {self.date_publication}'

    class Meta:
        ordering = ['date_publication']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
