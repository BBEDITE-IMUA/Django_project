"""
This module contains the views for the application.

Each function in this module corresponds to a different page or API endpoint.
These functions take a web request and return a web response.
This response can be the HTML contents of a document, a redirect,
a 404 error, an XML document, an image... or really anything, depending on the function.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CommentForm, StudentForm, TaskForm, TaskStudentForm
from .models import Comment, Student, Task, TaskStudent
from .serializers import (CommentSerializer, StudentSerializer, TaskSerializer,
                          TaskStudentSerializer)

ERROR = 'error'
TITLE = 'title'
TASK = 'task'
STUDENT = 'student'
COMMENT = 'comment'
FORM = 'form'
POST = 'POST'


class UserAdminPermission(permissions.BasePermission):
    """Allows access to secure methods only for authenticated users."""

    _safe_methods = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):
        """
        Check if the user is authenticated.

        Args:
            request (Request): The request object.
            view (View): The view object.

        Returns:
            bool: True if the user is authenticated.
        """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, object_to_check):
        """
        Check if the request is a safe method or if the user is staff or the owner of the object.

        Args:
            request (Request): The request object.
            view (View): The view object.
            object_to_check (Object): The object to check permissions for.

        Returns:
            bool: True if the request is a safe method or if the user is staff or the owner of the object.
        """
        if request.method in self._safe_methods:
            return True
        return request.user.is_staff or object_to_check.user == request.user


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint that allows tasks to be viewed or edited."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """
        Save the user who created the task when creating a new task.

        Args:
            serializer (serializers.Serializer): The serializer object.
        """
        serializer.save(user=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    """API endpoint that allows students to be viewed or edited."""

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """
        Save the user who created the student when creating a new student.

        Args:
            serializer (serializers.Serializer): The serializer object.
        """
        serializer.save(user=self.request.user)


class TaskStudentViewSet(viewsets.ModelViewSet):
    """API endpoint that allows task-student associations to be viewed or edited."""

    queryset = TaskStudent.objects.all()
    serializer_class = TaskStudentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """
        Save the task-student association when creating a new association.

        Args:
            serializer (serializers.Serializer): The serializer object.
        """
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    """API endpoint that allows comments to be viewed or edited."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        """
        Save the student who created the comment when creating a new comment.

        Args:
            serializer (serializers.Serializer): The serializer object.
        """
        student = Student.objects.get(user=self.request.user)
        serializer.save(student=student)


class UserRegistrationView(APIView):
    """API endpoint that allows users to register."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Register a new user.

        Args:
            request (Request): The request object.

        Returns:
            Response: The token of the new user.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({ERROR: 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(username=username, password=password)
            token = Token.objects.create(user=user)
        else:
            return Response({ERROR: 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Render the registration page.

        Args:
            request (Request): The request object.

        Returns:
            HttpResponse: The registration page.
        """
        return render(request, 'register.html')


class UserLoginView(APIView):
    """API endpoint that allows users to log in."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Log in a user.

        Args:
            request (Request): The request object.

        Returns:
            Response: The token of the logged-in user.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({ERROR: 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({ERROR: 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({ERROR: 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            token, _ = Token.objects.get_or_create(user=user)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Render the login page.

        Args:
            request (Request): The request object.

        Returns:
            HttpResponse: The login page.
        """
        return render(request, 'login.html')


def log_out(request):
    """
    Log out the user and redirect to the main page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The main page.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect('main_page')


def main_page(request):
    """
    Render the main page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The main page.
    """
    pages = {
        'Задачи': 'tasks_page',
        'Студенты': 'students_page',
        'Регистрация': 'register',
        'Получить токен': 'api_token',
    }
    return render(request, 'main.html', context={'page': pages, TITLE: 'Главная страница', 'user': request.user})


def tasks_page(request):
    """
    Render the tasks page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The tasks page.
    """
    context = {'tasks': Task.objects.all(), TITLE: 'Задачи'}
    return render(request, 'tasks.html', context=context)


def task_page(request, task_id):
    """
    Render the task page.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The task page.
    """
    context = {TASK: Task.objects.get(id=task_id), TITLE: 'Задача'}
    return render(request, 'entities/task.html', context=context)


def students_page(request):
    """
    Render the students page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The students page.
    """
    context = {'students': Student.objects.all(), TITLE: 'Студенты'}
    return render(request, 'students.html', context=context)


def student_page(request, student_id):
    """
    Render the student page.

    Args:
        request (Request): The request object.
        student_id (int): The id of the student.

    Returns:
        HttpResponse: The student page.
    """
    context = {STUDENT: Student.objects.get(id=student_id), TITLE: 'Студент'}
    return render(request, 'entities/student.html', context=context)


def comments_page(request):
    """
    Render the comments page.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The comments page.
    """
    context = {'comments': Comment.objects.all(), TITLE: 'Комментарии'}
    return render(request, 'comments.html', context=context)


def comment_page(request, comment_id):
    """
    Render the comment page.

    Args:
        request (Request): The request object.
        comment_id (int): The id of the comment.

    Returns:
        HttpResponse: The comment page.
    """
    context = {COMMENT: Comment.objects.get(id=comment_id), TITLE: 'Комментарий'}
    return render(request, 'entities/comment.html', context=context)


def create_task_view(request):
    """
    Create a new task.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The create task page.
    """
    if request.user.is_authenticated:
        if request.method == POST:
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.user = request.user
                task.save()
                return redirect('tasks_page')
        else:
            form = TaskForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы создать задачу')
        form = TaskForm()
    context = {FORM: form, TITLE: 'Создать задачу'}
    return render(request, 'forms/create_task.html', context=context)


def handle_post_requests(request, form, task, has_solve):
    """
    Handle POST request.

    Args:
        request (Request): The request object.
        form (Form): The form object.
        task (Task): The task object.
        has_solve (bool): The flag indicating if the task has been solved.

    Returns:
        HttpResponse or None: The task page or None.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему и создать студента, чтобы решить задачу')
        return None

    if form.is_valid() and not has_solve:
        task_student = form.save(commit=False)
        students = Student.objects.filter(user=request.user)
        if students:
            student = students[0]
            task_student.student = student
            task_student.solution = form.cleaned_data['solution']
            task_student.save()
            return redirect(TASK, task_id=task.id)
        else:
            messages.error(request, 'У вас нет связанных студентов')
    else:
        messages.error(request, 'Некорректные данные формы. Или вы уже решили эту задачу')
    return None


def create_form(request, task):
    """
    Create a form.

    Args:
        request (Request): The request object.
        task (Task): The task object.

    Returns:
        Form: The form object.
    """
    if request.user.is_authenticated:
        students = Student.objects.filter(user=request.user)
        if students:
            student = students[0]
            initial = {TASK: task, STUDENT: student}
            form = TaskStudentForm(initial=initial)
        else:
            form = TaskStudentForm(initial={TASK: task})
    else:
        form = TaskStudentForm(initial={TASK: task})
    return form


def complete_task(request, task_id):
    """
    Complete the task.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The task completion page.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему и создать студента, чтобы решить задачу')

    task = get_object_or_404(Task, id=task_id)
    students = None
    if request.user.is_authenticated:
        students = Student.objects.filter(user=request.user)
    if students:
        student = students[0]
        has_solve = TaskStudent.objects.filter(task=task, student=student).exists()
    else:
        has_solve = False

    if request.method == POST:
        form = TaskStudentForm(request.POST)
        response = handle_post_requests(request, form, task, has_solve)
        if response is not None:
            return response
    else:
        form = create_form(request, task)

    if request.user.is_authenticated:
        if request.user.is_superuser:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(user=request.user)
    else:
        students = None

    tasks = Task.objects.all()
    context = {
        FORM: form,
        'students': students,
        'tasks': tasks,
        'task_id': task_id,
        TITLE: 'Завершить задачу',
        TASK: task,
        'has_solve': has_solve,
    }
    return render(request, 'complete_task.html', context)


def task_solutions(request, task_id):
    """
    Render the task solutions page.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The task solutions page.
    """
    task = get_object_or_404(Task, id=task_id)
    solutions = TaskStudent.objects.filter(task=task)
    return render(request, 'task_solutions.html', {'solutions': solutions})


def delete_task(request, task_id):
    """
    Delete the task.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The tasks page.
    """
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_staff or task.user == request.user:
        task.delete()
        return redirect('tasks_page')
    return redirect(TASK, task_id=task.id)


def put_task(request, task_id):
    """
    Update the task.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The update task page.
    """
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_staff or task.user == request.user:
        if request.method == POST:
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect(TASK, task_id=task.id)
        else:
            form = TaskForm(instance=task)
    else:
        messages.error(request, 'У вас нет прав на изменение этой задачи')
        form = TaskForm(instance=task)
    context = {FORM: form, TITLE: 'Изменить задачу', TASK: task}
    return render(request, 'update/put_task.html', context)


def create_comment(request, task_id):
    """
    Create a new comment.

    Args:
        request (Request): The request object.
        task_id (int): The id of the task.

    Returns:
        HttpResponse: The create comment page.
    """
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему, чтобы создать комментарий')

    task = get_object_or_404(Task, id=task_id)
    if request.user.is_authenticated and request.method == POST:
        post_data = request.POST.copy()
        post_data.update({'task_id': task.id})
        form = CommentForm(post_data)
        if form.is_valid():
            form.save()
            return redirect('comments_page')
        else:
            messages.error(request, 'Некорректные данные формы')
    else:
        form = CommentForm()

    students = None
    if request.user.is_authenticated:
        students = Student.objects.filter(user=request.user)
    tasks = Task.objects.all()
    context = {FORM: form, TASK: task, 'students': students, 'tasks': tasks, TITLE: 'Создать комментарий'}
    return render(request, 'forms/create_comment.html', context)


def delete_comment(request, comment_id):
    """
    Delete the comment.

    Args:
        request (Request): The request object.
        comment_id (int): The id of the comment.

    Returns:
        HttpResponse: The comments page.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff or comment.student.user == request.user:
        comment.delete()
        return redirect('comments_page')
    messages.error(request, 'У вас нет прав на удаление этого комментария')
    return redirect(COMMENT, comment_id=comment.id)


def put_comment(request, comment_id):
    """
    Update the comment.

    Args:
        request (Request): The request object.
        comment_id (int): The id of the comment.

    Returns:
        HttpResponse: The update comment page.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff or comment.student.user == request.user:
        if request.method == POST:
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                return redirect(COMMENT, comment_id=comment.id)
        else:
            form = CommentForm(instance=comment)
    else:
        messages.error(request, 'У вас нет прав на изменение этого комментария')
        form = CommentForm(instance=comment)
    context = {FORM: form, TITLE: 'Изменить комментарий', COMMENT: comment}
    return render(request, 'update/put_comment.html', context)


def handle_post_request(request, form):
    """
    Handle POST request.

    Args:
        request (Request): The request object.
        form (Form): The form object.

    Returns:
        HttpResponse: The create student page or redirect.
    """
    if form.is_valid():
        if not request.user.is_staff and Student.objects.filter(user=request.user).exists():
            messages.error(request, 'Вы уже создали студента')
        else:
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('students_page')
    return None


def create_student(request):
    """
    Create a new student.

    Args:
        request (Request): The request object.

    Returns:
        HttpResponse: The create student page.
    """
    if request.user.is_authenticated:
        if request.method == POST:
            form = StudentForm(request.POST)
            response = handle_post_request(request, form)
            if response is not None:
                return response
        else:
            form = StudentForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы создать студента')
        form = StudentForm()

    context = {FORM: form, TITLE: 'Создать студента'}
    return render(request, 'forms/create_student.html', context)


def delete_student(request, student_id):
    """
    Delete the student.

    Args:
        request (Request): The request object.
        student_id (int): The id of the student.

    Returns:
        HttpResponse: The students page.
    """
    student = get_object_or_404(Student, id=student_id)
    if request.user.is_staff or student.user == request.user:
        student.delete()
        return redirect('students_page')
    messages.error(request, 'У вас нет прав на удаление этого студента')
    return redirect(STUDENT, student_id=student.id)


def put_student(request, student_id):
    """
    Update the student.

    Args:
        request (Request): The request object.
        student_id (int): The id of the student.

    Returns:
        HttpResponse: The update student page.
    """
    student = get_object_or_404(Student, id=student_id)
    if request.user.is_staff or student.user == request.user:
        if request.method == POST:
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                return redirect(STUDENT, student_id=student.id)
        else:
            form = StudentForm(instance=student)
    else:
        messages.error(request, 'У вас нет прав на изменение этого студента')
        form = StudentForm(instance=student)
    context = {FORM: form, TITLE: 'Изменить студента', STUDENT: student}
    return render(request, 'update/put_student.html', context)
