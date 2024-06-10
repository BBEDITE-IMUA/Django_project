from django.test import TestCase, Client, RequestFactory
from rest_framework.test import APIClient
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.authtoken.models import Token
from main.models import Task, Student, Comment, TaskStudent
import datetime
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .views import UserAdminPermission
from rest_framework import status
from main.views import tasks_page, task_page, students_page, student_page, comments_page, comment_page, main_page
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import validate_difficulty_range, max_length
from .forms import StudentForm, TaskForm, CommentForm, TaskStudentForm


class TestTask(TestCase):
    _user_creds = {'username': 'abc', 'password': '123'}
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(**self._user_creds)
        self.tocken = Token(user=self.user)
        self.client.force_authenticate(user=self.user, token=self.tocken)
        self.superuser = User.objects.create_superuser(username='superuser', password='password')
        self.client.force_authenticate(user=self.superuser, token=Token.objects.create(user=self.superuser))
        self.task = Task.objects.create(name='Task 1', difficulty=1, user=self.superuser)
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.superuser)
        self.comment = Comment.objects.create(task_id=self.task, date_publication='2022-12-12', text_comment='Comment 1', student=self.student)

    def test_task_list(self):
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, 200)

    def test_task_create(self):
        response = self.client.post('/api/v1/tasks/', {'name': 'Task 1', 'description': 'sss', 'difficulty': 1})
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertIn(response.data['id'], [str(task.id) for task in Task.objects.all()])

    def test_task_update(self):
        response = self.client.put(f'/api/v1/tasks/{self.task.id}/', {'name': 'Task 1', 'description': 'sss', 'difficulty': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertEqual(Task.objects.get(name = 'Task 1').difficulty, 1)
        self.assertEqual(Task.objects.get(description = 'sss').difficulty, 1)
        self.assertEqual(Task.objects.get(name = 'Task 1').description, 'sss')

    def test_task_delete(self):
        response = self.client.delete(f'/api/v1/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, 204)



    def test_student_list(self):
        response = self.client.get('/api/v1/students/')
        self.assertEqual(response.status_code, 200)
    
    def test_student_create(self):
        response = self.client.post('/api/v1/students/', {'nickname': 'Student 1', 'registration_date': '2023-12-12'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertIn(response.data['id'], [str(student.id) for student in Student.objects.all()])

    def test_student_update(self):
        response = self.client.put(f'/api/v1/students/{self.student.id}/', {'nickname': 'Student 1', 'registration_date': '2022-12-12'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertEqual(Student.objects.get(nickname = 'Student 1').registration_date, datetime.datetime.strptime('2022-12-12', '%Y-%m-%d').date())

    def test_student_delete(self):
        response = self.client.delete(f'/api/v1/students/{self.student.id}/')
        self.assertEqual(response.status_code, 204)



    def test_comment_list(self):
        response = self.client.get('/api/v1/comments/')
        self.assertEqual(response.status_code, 200)

    def test_comment_create(self):
        response = self.client.post('/api/v1/comments/', {'task_id': self.task.id, 'student': self.student.id, 'text_comment': 'Comment 1', 'date_publication': '2022-12-12'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertIn(response.data['id'], [str(comment.id) for comment in Comment.objects.all()])

    def test_comment_update(self):
        response = self.client.put(f'/api/v1/comments/{self.comment.id}/', {'task_id': self.task.id, 'student': self.student.id,  'date_publication': '2022-12-12','text_comment': 'Comment 2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertEqual(Comment.objects.get(text_comment = 'Comment 2').task_id, self.task)
        self.assertEqual(Comment.objects.get(text_comment = 'Comment 2').date_publication, datetime.datetime.strptime('2022-12-12', '%Y-%m-%d').date())
        self.assertEqual(Comment.objects.get(date_publication = datetime.datetime.strptime('2022-12-12', '%Y-%m-%d').date()).text_comment, 'Comment 2')

    def test_comment_delete(self):
        response = self.client.delete(f'/api/v1/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())



    def test_task_student_list(self):
        response = self.client.get('/api/v1/task_students/')
        self.assertEqual(response.status_code, 200)

    def test_create_task_student(self):
        response = self.client.post('/api/v1/task_students/', {'task': self.task.id, 'student': self.student.id, 'solution': 'Solution 1'})
        self.assertEqual(response.status_code, 201)

    
    def test_user_already_exists(self):
        response = self.client.post('/register/', {'username': 'abc', 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'User already exists'})

class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.student = Student.objects.create(user=self.user, nickname='Student 1', registration_date=date.today())
        self.task = Task.objects.create(name='Task 1', difficulty=1, user=self.user)
        self.comment = Comment.objects.create(task_id=self.task, date_publication=date.today(), text_comment='Comment 1', student=self.student)
        self.task2 = Task.objects.create(name='Task 2', difficulty=2, user=self.user)
        self.task3 = Task.objects.create(name='Task 3', difficulty=3, user=self.user)
        TaskStudent.objects.create(student=self.student, task=self.task, solution='Solution 1')
        TaskStudent.objects.create(student=self.student, task=self.task2, solution='Solution 2')
        TaskStudent.objects.create(student=self.student, task=self.task3, solution='Solution 3')

    def test_registration_date_in_future_raises_error(self):
        future_date = date.today() + timedelta(days=1)
        student = Student(user=self.user, nickname='Student 1', registration_date=future_date)
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_task_solutions(self):
        response = self.client.get(reverse('task_solutions', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    def test_rating(self):
        self.assertEqual(self.student.rating, 2)

    def test_validate_difficulty_range_invalid(self):
        with self.assertRaises(ValidationError):
            validate_difficulty_range(6)

    def test_max_length_invalid(self):
        with self.assertRaises(ValidationError):
            max_length('a' * 101)

    def test_str_task(self):
        self.assertEqual(str(self.task), 'Task 1')
    
    def test_str_student(self):
        self.assertEqual(str(self.student), 'Student 1')

    def test_str_comment(self):
        self.assertEqual(str(self.comment), f'Comment by Task 1 at {date.today()}')


class UserRegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_new_user(self):
        response = self.client.post('/register/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(username='testuser')
        self.assertIsNotNone(user)
        token = Token.objects.get(user=user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_registration_no_username(self):
        response = self.client.post('/register/', {'password': 'testpass'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username and password are required'})

    def test_logout_authenticated_user(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.force_login(user)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_unauthenticated_user(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_get_registration(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_create_task_view(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('create_task'), data={
            'name': 'Test Task',
            'description': 'Test Description',
            'difficulty': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), initial_task_count + 1)
        response = self.client.get(reverse('create_task'))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_task(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        task = Task.objects.create(name='Task 1', difficulty=1, user=user)
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), initial_task_count - 1)
    
    def test_put_task(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        task = Task.objects.create(name='Task 1', difficulty=1, user=user)
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('put_task', args=[task.id]), data={
            'name': 'Test Task',
            'description': 'Test Description',
            'difficulty': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), initial_task_count)
        response = self.client.get(reverse('put_task', args=[task.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_comment(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        task = Task.objects.create(name='Task 1', difficulty=1, user=user)
        student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=user)
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse('create_comment', args=[task.id]), data={
            'task_id': task.id,
            'student': student.id,
            'text_comment': 'Test Comment',
            'date_publication': '2022-12-12',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), initial_comment_count + 1)
        response = self.client.get(reverse('create_comment', args=[task.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_delete_comment(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        task = Task.objects.create(name='Task 1', difficulty=1, user=user)
        student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=user)
        comment = Comment.objects.create(task_id=task, date_publication='2022-12-12', text_comment='Comment 1', student=student)
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse('delete_comment', args=[comment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), initial_comment_count - 1)

    def test_put_comment(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        task = Task.objects.create(name='Task 1', difficulty=1, user=user)
        student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=user)
        comment = Comment.objects.create(task_id=task, date_publication='2022-12-12', text_comment='Comment 1', student=student)
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse('put_comment', args=[comment.id]), data={
            'task_id': task.id,
            'student': student.id,
            'text_comment': 'Test Comment',
            'date_publication': '2022-12-12',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), initial_comment_count)
        response = self.client.get(reverse('put_comment', args=[comment.id]))
        self.assertEqual(response.status_code, 200)


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass')

    def test_login_no_username_password(self):
        response = self.client.post(reverse('login'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username and password are required'})

    def test_login_no_user(self):
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'pass'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'User does not exist'})

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'wrong'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Wrong password'})

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'pass'})
        self.assertEqual(response.status_code, 200)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_get_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')


class UserAdminPermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = UserAdminPermission()
        self.view = None
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_has_object_permission(self):
        request = self.factory.get('/')
        request.user = self.user
        obj = None
        self.assertTrue(self.permission.has_object_permission(request, self.view, obj))

# def add_test_page(name: str, func):
#     def decorator(cls):
#         def test_func(self):
#             request = self.factory.get(f'/{name}')
#             response = func(request)
#             self.assertEqual(response.status_code, 200)
#         setattr(cls, f'test_{name}', test_func)
#         return cls
#     return decorator

# @add_test_page('tasks', tasks_page)
# @add_test_page('students', students_page)
# @add_test_page('comments', comments_page)
# @add_test_page('main_page', main_page)

class ViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = Task.objects.create(name='Task 1', difficulty=1, user=self.user)
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.comment = Comment.objects.create(task_id=self.task, date_publication='2022-12-12', text_comment='Comment 1', student=self.student)

    def test_tasks_page(self):
        request = self.factory.get('/tasks')
        response = tasks_page(request)
        self.assertEqual(response.status_code, 200)

    def test_task_page(self):
        request = self.factory.get(f'/task/{self.task.id}')
        response = task_page(request, self.task.id)
        self.assertEqual(response.status_code, 200)

    def test_students_page(self):
        request = self.factory.get('/students')
        response = students_page(request)
        self.assertEqual(response.status_code, 200)

    def test_student_page(self):
        request = self.factory.get(f'/student/{self.student.id}')
        response = student_page(request, self.student.id)
        self.assertEqual(response.status_code, 200)

    def test_comments_page(self):
        request = self.factory.get('/comments')
        response = comments_page(request)
        self.assertEqual(response.status_code, 200)

    def test_comment_page(self):
        request = self.factory.get(f'/comment/{self.comment.id}')
        response = comment_page(request, self.comment.id)
        self.assertEqual(response.status_code, 200)

    def test_main_page(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        response = main_page(request)
        self.assertEqual(response.status_code, 200)

class StudentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.student_data = {'nickname': 'Student 1', 'registration_date': '2022-12-12', 'user': self.user.id}
        self.student_form = StudentForm(data=self.student_data)

    def test_create_student(self):
        self.client.login(username='testuser', password='testpass')
        form = self.student_form
        if form.is_valid():
            response = self.client.post(reverse('create_student'), data=form.cleaned_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('students_page'))

    def test_create_student_get_form(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('create_student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forms/create_student.html')

    def test_put_student_get_form(self):
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('put_student', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update/put_student.html')

    def test_create_student_duplicate(self):
        self.client.login(username='testuser', password='testpass')
        Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        response = self.client.post(reverse('create_student'), data={'nickname': 'Student 1', 'registration_date': '2022-12-12', 'user': self.user.id})
        self.assertContains(response, 'Вы уже создали студента')


    def test_delete_student(self):
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete_student', args=[self.student.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('students_page'))

    def test_put_student(self):
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.client.login(username='testuser', password='testpass')
        form = self.student_form
        if form.is_valid():
            response = self.client.post(reverse('put_student', args=[self.student.id]), data=form.cleaned_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('student', args=[self.student.id]))
        
    def test_create_student_not_authenticated(self):
        response = self.client.post(reverse('create_student'), data=self.student_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать студента')

    def test_delete_student_no_permission(self):
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_student', args=[self.student.id]), follow=True)
        self.assertRedirects(response, expected_url=reverse('student', args=[self.student.id]), status_code=302, target_status_code=200)
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого студента')

    def test_put_student_no_permission(self):
        self.student = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('put_student', args=[self.student.id]), data=self.student_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'У вас нет прав на изменение этого студента')
    
    def test_unauthenticated_user(self):
        response = self.client.get(reverse('create_task'))
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Вы должны войти в систему, чтобы создать задачу')

class CommentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.task = Task.objects.create(name='Task 1', difficulty=1, user=self.user1)
        self.student1 = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user1)
        self.student2 = Student.objects.create(nickname='Student 2', registration_date='2022-12-12', user=self.user2)
        self.comment = Comment.objects.create(task_id=self.task, date_publication='2022-12-12', text_comment='Comment 1', student=self.student1)

    def test_create_comment_not_authenticated(self):
        response = self.client.post(reverse('create_comment', args=[self.task.id]))
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать комментарий')

    def test_delete_comment_no_permission(self):
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]), follow=True)
        self.assertRedirects(response, expected_url=reverse('comment', args=[self.comment.id]), status_code=302, target_status_code=200)
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого комментария')

    def test_put_comment_no_permission(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('put_comment', args=[self.comment.id]))
        self.assertContains(response, 'У вас нет прав на изменение этого комментария')

    def test_form_no_valid(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('create_comment', args=[self.task.id]), data={})
        self.assertContains(response, 'Некорректные данные формы')

class CompleteTaskViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.task = Task.objects.create(name='Task 1', difficulty=1, user=self.user1)
        self.student1 = Student.objects.create(nickname='Student 1', registration_date='2022-12-12', user=self.user1)
        self.student2 = Student.objects.create(nickname='Student 2', registration_date='2022-12-12', user=self.user2)

    def test_complete_task_not_authenticated(self):
        response = self.client.post(reverse('complete_task', args=[self.task.id]))
        self.assertContains(response, 'Вы должны войти в систему и создать студента, чтобы решить задачу')

    def test_complete_task_authenticated_with_student_invalid_form(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('complete_task', args=[self.task.id]), data={})
        self.assertContains(response, 'Некорректные данные формы. Или вы уже решили эту задачу')

    def test_complete_task_authenticated_with_student_valid_form(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(reverse('complete_task', args=[self.task.id]), data={'task': self.task.id, 'student': self.student1.id, 'solution': 'Solution 1'})
        self.assertRedirects(response, reverse('task', args=[self.task.id]))

    def test_complete_task_authenticated_with_student_get_request(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('complete_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Завершить задачу')

    def test_complete_task_authenticated_no_student_get_request(self):
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('complete_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Завершить задачу')

    def test_complete_task_not_authenticated_get_request(self):
        response = self.client.get(reverse('complete_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Завершить задачу')
    
    def test_delete_task_no_permission(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(reverse('delete_task', args=[self.task.id]))
        self.assertRedirects(response, reverse('task', args=[self.task.id]))

    def test_put_task_no_permission(self):
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('put_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'У вас нет прав на изменение этой задачи')
        self.assertEqual(response.context['form'].instance, self.task)