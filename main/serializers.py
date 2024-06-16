"""
This module defines the serializers for the application.

It includes serializers for tasks, students, task-student associations, and comments.
Each serializer is a Django REST Framework ModelSerializer,
which means it automatically generates fields based on the model it's serializing.
"""

from rest_framework import serializers

from .models import Comment, Student, Task, TaskStudent

USER_USERNAME = 'user.username'
ALL_FIELDS = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model."""

    user = serializers.ReadOnlyField(source=USER_USERNAME)

    class Meta:
        model = Task
        fields = ALL_FIELDS


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the Student model."""

    user = serializers.ReadOnlyField(source=USER_USERNAME)

    class Meta:
        model = Student
        fields = ALL_FIELDS


class TaskStudentSerializer(serializers.ModelSerializer):
    """Serializer for the TaskStudent model."""

    user = serializers.ReadOnlyField(source=USER_USERNAME)

    class Meta:
        model = TaskStudent
        fields = ALL_FIELDS


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the Comment model."""

    user = serializers.ReadOnlyField(source=USER_USERNAME)

    class Meta:
        model = Comment
        fields = ALL_FIELDS
