# Generated by Django 5.0.3 on 2024-06-04 13:06

import datetime
import django.db.models.deletion
import main.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nickname', models.TextField(validators=[main.models.max_length])),
                ('registration_date', models.DateField(default=datetime.date.today, editable=False, validators=[main.models.validate_future_date])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Student',
                'verbose_name_plural': 'Students',
                'ordering': ['registration_date'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField(validators=[main.models.max_length])),
                ('description', models.TextField()),
                ('difficulty', models.IntegerField(default=0, validators=[main.models.validate_difficulty_range])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text_comment', models.TextField()),
                ('date_publication', models.DateField(default=datetime.date.today, editable=False, validators=[main.models.validate_future_date])),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_comments', to='main.student')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_comments', to='main.task')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['date_publication'],
            },
        ),
        migrations.CreateModel(
            name='TaskStudent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('solution', models.TextField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.student')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.task')),
            ],
            options={
                'verbose_name': 'TaskStudent',
                'verbose_name_plural': 'TaskStudents',
                'ordering': ['task'],
                'unique_together': {('task', 'student')},
            },
        ),
        migrations.AddField(
            model_name='task',
            name='students',
            field=models.ManyToManyField(through='main.TaskStudent', to='main.student'),
        ),
        migrations.AddField(
            model_name='student',
            name='tasks',
            field=models.ManyToManyField(through='main.TaskStudent', to='main.task'),
        ),
    ]
