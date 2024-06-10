"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main.views import *
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'students', StudentViewSet)
router.register(r'task_students', TaskStudentViewSet)
router.register(r'comments', CommentViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', log_out, name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('', main_page, name='main_page'),

    path('tasks/', tasks_page, name='tasks_page'),
    path('task/create/', create_task_view, name='create_task'),
    path('task/<str:task_id>/', task_page, name='task'),
    path('task/delete/<str:task_id>/', delete_task, name='delete_task'),
    path('task/update/<str:task_id>/', put_task, name='put_task'),
    path('complete_task/<uuid:task_id>/', complete_task, name='complete_task'),
    path('task_solutions/<uuid:task_id>/', task_solutions, name='task_solutions'),

    path('students/', students_page, name='students_page'),
    path('student/<str:student_id>/', student_page, name='student'),
    path('create_student/', create_student, name='create_student'),
    path('delete_student/<str:student_id>/', delete_student, name='delete_student'),
    path('update_student/<str:student_id>/', put_student, name='put_student'),

    path('comments/', comments_page, name='comments_page'),
    path('comment/<str:comment_id>/', comment_page, name='comment'),
    path('comment/create/<uuid:task_id>/', create_comment, name='create_comment'),
    path('comment/delete/<str:comment_id>/', delete_comment, name='delete_comment'),
    path('comment/update/<str:comment_id>/', put_comment, name='put_comment'),
]
