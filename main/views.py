from rest_framework import viewsets
from .models import Task, Student, TaskStudent, Comment
from .serializers import TaskSerializer, StudentSerializer, TaskStudentSerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskForm, CommentForm, StudentForm, TaskStudentForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import QueryDict


# request.user.is_staff - администратор
# obj.user - пользователь, создавший объект
# request.user.is_authenticated - авторизованный пользователь
# request.user - текущий пользователь


class UserAdminPermission(permissions.BasePermission):
    _safe_methods = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in self._safe_methods:
            return True
        return request.user.is_staff or obj.user == request.user

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskStudentViewSet(viewsets.ModelViewSet):
    queryset = TaskStudent.objects.all()
    serializer_class = TaskStudentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        serializer.save


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [UserAdminPermission]

    def perform_create(self, serializer):
        student = Student.objects.get(user=self.request.user)
        serializer.save(student=student)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(username=username, password=password)
            token = Token.objects.create(user=user)
        else:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    
    def get(self, request):
        return render(request, 'register.html')

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
            token, _ = Token.objects.get_or_create(user=user)
        login(request=request, user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    
    def get(self, request):
        return render(request, 'login.html')


    
def log_out(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('main_page')

    
def main_page(request):
    pages = {
        'Задачи': 'tasks_page',
        'Студенты': 'students_page',
        'Регистрация': 'register',
        'Получить токен': 'api_token',
    }
    return render(request, 'main.html', context={'page': pages, 'title': 'Главная страница' , 'user': request.user})

def tasks_page(request):
    return render(request, 'tasks.html', context={'tasks': Task.objects.all(), 'title': 'Задачи'})

def task_page(request, task_id):
    return render(request, 'entities/task.html', context={'task': Task.objects.get(id=task_id), 'title': 'Задача'})


def students_page(request):
    return render(request, 'students.html', context={'students': Student.objects.all(), 'title': 'Студенты'})

def student_page(request, student_id):
    return render(request, 'entities/student.html', context={'student': Student.objects.get(id=student_id), 'title': 'Студент'})


def comments_page(request):
    return render(request, 'comments.html', context={'comments': Comment.objects.all(), 'title': 'Комментарии'})

def comment_page(request, comment_id):
    return render(request, 'entities/comment.html', context={'comment': Comment.objects.get(id=comment_id), 'title': 'Комментарий'})



def create_task_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
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
    return render(request, 'forms/create_task.html', context={'form': form, 'title': 'Создать задачу'})


def complete_task(request, task_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему и создать студента, чтобы решить задачу')

    task = get_object_or_404(Task, id=task_id)
    students = Student.objects.filter(user=request.user) if request.user.is_authenticated else None 
    if students:
        student = students[0]
        has_solve = TaskStudent.objects.filter(task=task, student=student).exists()
    else:
        has_solve = False

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Вы должны войти в систему и создать студента, чтобы решить задачу')
            form = TaskStudentForm()
        else:
            form = TaskStudentForm(request.POST)
            if form.is_valid() and not has_solve:
                task_student = form.save(commit=False)
                students = Student.objects.filter(user=request.user)
                if students:
                    student = students[0]
                    task_student.student = student
                    task_student.solution = form.cleaned_data['solution']
                    task_student.save()
                    return redirect('task', task_id=task.id)
                else:
                    messages.error(request, 'У вас нет связанных студентов')
            else:
                messages.error(request, 'Некорректные данные формы. Или вы уже решили эту задачу')
    else:
        if request.user.is_authenticated:
            students = Student.objects.filter(user=request.user)
            if students:
                student = students[0]
                form = TaskStudentForm(initial={'task': task, 'student': student})
            else:
                form = TaskStudentForm(initial={'task': task})
        else:
            form = TaskStudentForm(initial={'task': task})

    if request.user.is_authenticated:
        if request.user.is_superuser:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(user=request.user)
    else:
        students = None

    tasks = Task.objects.all()
    return render(request, 'complete_task.html', {'form': form, 'students': students, 'tasks': tasks, 'task_id': task_id, 'title': 'Завершить задачу', 'task': task, 'has_solve': has_solve})


def task_solutions(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    solutions = TaskStudent.objects.filter(task=task)
    return render(request, 'task_solutions.html', {'solutions': solutions})


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_staff or task.user == request.user:
        task.delete()
        return redirect('tasks_page')
    else:
        return redirect('task', task_id=task.id)
    
def put_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_staff or task.user == request.user:
        if request.method == 'POST':
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('task', task_id=task.id)
        else:
            form = TaskForm(instance=task)
    else:
        messages.error(request, 'У вас нет прав на изменение этой задачи')
        form = TaskForm(instance=task)
    return render(request, 'update/put_task.html', context={'form': form, 'title': 'Изменить задачу', 'task': task})




def create_comment(request, task_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Вы должны войти в систему, чтобы создать комментарий')
    
    task = get_object_or_404(Task, id=task_id)
    if request.user.is_authenticated and request.method == 'POST':
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
    students = Student.objects.filter(user=request.user) if request.user.is_authenticated else None
    tasks = Task.objects.all()
    return render(request, 'forms/create_comment.html', context={'form': form, 'task': task, 'students': students, 'tasks': tasks, 'title': 'Создать комментарий'})

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff or comment.student.user == request.user:
        comment.delete()
        return redirect('comments_page')
    else:
        messages.error(request, 'У вас нет прав на удаление этого комментария')
        return redirect('comment', comment_id=comment.id)
    
def put_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff or comment.student.user == request.user:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                return redirect('comment', comment_id=comment.id)
        else:
            form = CommentForm(instance=comment)
    else:
        messages.error(request, 'У вас нет прав на изменение этого комментария')
        form = CommentForm(instance=comment)
    return render(request, 'update/put_comment.html', context={'form': form, 'title': 'Изменить комментарий', 'comment': comment})



def create_student(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = StudentForm(request.POST)
            if form.is_valid():
                if not request.user.is_staff and Student.objects.filter(user=request.user).exists():
                    messages.error(request, 'Вы уже создали студента')
                else:
                    student = form.save(commit=False)
                    student.user = request.user
                    student.save()
                    return redirect('students_page')
        else:
            form = StudentForm()
    else:
        messages.error(request, 'Вы должны войти в систему, чтобы создать студента')
        form = StudentForm()

    return render(request, 'forms/create_student.html', context={'form': form, 'title': 'Создать студента'})

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.user.is_staff or student.user == request.user:
        student.delete()
        return redirect('students_page')
    else:
        messages.error(request, 'У вас нет прав на удаление этого студента')
        return redirect('student', student_id=student.id)
    
def put_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.user.is_staff or student.user == request.user:
        if request.method == 'POST':
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                return redirect('student', student_id=student.id)
        else:
            form = StudentForm(instance=student)
    else:
        messages.error(request, 'У вас нет прав на изменение этого студента')
        form = StudentForm(instance=student)
    return render(request, 'update/put_student.html', context={'form': form, 'title': 'Изменить студента', 'student': student})