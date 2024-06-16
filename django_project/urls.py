"""
This module defines the URL routes for the Django application.

The routes are defined in the `urlpatterns` list. Django will use this list to route requests based on the URL.

The module also sets up a default router for the Django Rest Framework (DRF) and registers several viewsets with it.

The DRF router will automatically generate appropriate URLs for the registered viewsets.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from main import views

router = routers.DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'task_students', views.TaskStudentViewSet)
router.register(r'comments', views.CommentViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('', views.main_page, name='main_page'),

    path('tasks/', views.tasks_page, name='tasks_page'),
    path('task/create/', views.create_task_view, name='create_task'),
    path('task/<str:task_id>/', views.task_page, name='task'),
    path('task/delete/<str:task_id>/', views.delete_task, name='delete_task'),
    path('task/update/<str:task_id>/', views.put_task, name='put_task'),
    path('complete_task/<uuid:task_id>/', views.complete_task, name='complete_task'),
    path('task_solutions/<uuid:task_id>/', views.task_solutions, name='task_solutions'),

    path('students/', views.students_page, name='students_page'),
    path('student/<str:student_id>/', views.student_page, name='student'),
    path('create_student/', views.create_student, name='create_student'),
    path('delete_student/<str:student_id>/', views.delete_student, name='delete_student'),
    path('update_student/<str:student_id>/', views.put_student, name='put_student'),

    path('comments/', views.comments_page, name='comments_page'),
    path('comment/<str:comment_id>/', views.comment_page, name='comment'),
    path('comment/create/<uuid:task_id>/', views.create_comment, name='create_comment'),
    path('comment/delete/<str:comment_id>/', views.delete_comment, name='delete_comment'),
    path('comment/update/<str:comment_id>/', views.put_comment, name='put_comment'),
]
