"""This module contains tests for the API."""

import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from main.models import Comment, Student, Task, TaskStudent
from main.views import (comment_page, comments_page, main_page, student_page,
                        students_page, task_page, tasks_page)

from .forms import StudentForm
from .models import max_length, validate_difficulty_range
from .views import UserAdminPermission

API_V1_TASKS = '/api/v1/tasks/'
API_V1_STUDENTS = '/api/v1/students/'
API_V1_COMMENTS = '/api/v1/comments/'
REGISTER = '/register/'
USERNAME = 'username'
PASSWORD = 'password'
TASK = 'task'
TASK_FIRST = 'Task 1'
TASK_ID = 'task_id'
COMPLETE_TASK = 'complete_task'
STUDENT = 'student'
STUDENT_FIRST = 'Student 1'
CREATE_STUDENT = 'create_student'
COMMENT = 'comment'
COMMENT_FIRST = 'Comment 1'
CREATE_COMMENT = 'create_comment'
TEST_DATA = '2022-12-12'
INT_PASSWORD = '12345'
TEST_PASSWORD = 'testpass'
PASS = 'pass'
NICKNAME = 'nickname'
NAME = 'name'
USER = 'user'
USER_FIRST = 'user1'
USER_LAST = 'user2'
LOGIN = 'login'
TEST_USER = 'testuser'
ERROR = 'error'
DESCRIPTION = 'description'
DISC = 'disc'
DIFFICULTY = 'difficulty'
REGISTRATION_DATE = 'registration_date'
DATE_PUBLICATION = 'date_publication'
TEXT_COMMENT = 'text_comment'
ID = 'id'
MAIN_PAGE = '/'


class TestTask(TestCase):
    """Test Task model."""

    _user_creds = {USERNAME: 'abc', PASSWORD: '123'}

    def setUp(self):
        """Set up test data for Task model."""
        self.client = APIClient()
        self.user = User.objects.create(**self._user_creds)
        self.tocken = Token(user=self.user)
        self.client.force_authenticate(user=self.user, token=self.tocken)
        self.superuser = User.objects.create_superuser(username='superuser', password=PASSWORD)
        self.client.force_authenticate(user=self.superuser, token=Token.objects.create(user=self.superuser))
        self.task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=self.superuser)
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.superuser)
        self.comment = Comment.objects.create(
            task_id=self.task,
            date_publication=TEST_DATA,
            text_comment=COMMENT_FIRST,
            student=self.student,
        )

    def test_task_list(self):
        """Test task list."""
        response = self.client.get(API_V1_TASKS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_create(self):
        """Test task create."""
        response = self.client.post(API_V1_TASKS, {NAME: TASK_FIRST, DESCRIPTION: DISC, DIFFICULTY: 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(ID, response.data)
        self.assertIn(response.data[ID], [str(task.id) for task in Task.objects.all()])

    def test_task_update(self):
        """Test task update."""
        response = self.client.put(
            f'/api/v1/tasks/{self.task.id}/',
            {NAME: TASK_FIRST, DESCRIPTION: DISC, DIFFICULTY: 1},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ID, response.data)
        self.assertEqual(Task.objects.get(name=TASK_FIRST).difficulty, 1)
        self.assertEqual(Task.objects.get(description=DISC).difficulty, 1)
        self.assertEqual(Task.objects.get(name=TASK_FIRST).description, DISC)

    def test_task_delete(self):
        """Test task delete."""
        response = self.client.delete(f'/api/v1/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_list(self):
        """Test student list."""
        response = self.client.get(API_V1_STUDENTS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_create(self):
        """Test student create."""
        response = self.client.post(API_V1_STUDENTS, {NICKNAME: STUDENT_FIRST, REGISTRATION_DATE: '2023-12-12'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(ID, response.data)
        self.assertIn(response.data[ID], [str(student.id) for student in Student.objects.all()])

    def test_student_update(self):
        """Test student update."""
        response = self.client.put(
            f'/api/v1/students/{self.student.id}/',
            {NICKNAME: STUDENT_FIRST, REGISTRATION_DATE: TEST_DATA},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ID, response.data)
        self.assertEqual(
            Student.objects.get(nickname=STUDENT_FIRST).registration_date,
            datetime.datetime.strptime(TEST_DATA, '%Y-%m-%d').date(),
        )

    def test_student_delete(self):
        """Test student delete."""
        response = self.client.delete(f'/api/v1/students/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_list(self):
        """Test comment list."""
        response = self.client.get(API_V1_COMMENTS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_create(self):
        """Test comment create."""
        response = self.client.post(
            API_V1_COMMENTS,
            {
                TASK_ID: self.task.id,
                STUDENT: self.student.id,
                TEXT_COMMENT: COMMENT_FIRST,
                DATE_PUBLICATION: TEST_DATA,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(ID, response.data)
        self.assertIn(response.data[ID], [str(comment.id) for comment in Comment.objects.all()])

    def test_comment_update(self):
        """Test comment update."""
        response = self.client.put(
            f'/api/v1/comments/{self.comment.id}/',
            {
                TASK_ID: self.task.id,
                STUDENT: self.student.id,
                DATE_PUBLICATION: TEST_DATA,
                TEXT_COMMENT: 'Comment 2',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ID, response.data)
        self.assertEqual(Comment.objects.get(text_comment='Comment 2').task_id, self.task)
        self.assertEqual(
            Comment.objects.get(text_comment='Comment 2').date_publication,
            datetime.datetime.strptime(TEST_DATA, '%Y-%m-%d').date(),
        )
        self.assertEqual(Comment.objects.get(
            date_publication=datetime.datetime.strptime(TEST_DATA, '%Y-%m-%d').date(),
            ).text_comment, 'Comment 2',
        )

    def test_comment_delete(self):
        """Test comment delete."""
        response = self.client.delete(f'/api/v1/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_task_student_list(self):
        """Test task student list."""
        response = self.client.get('/api/v1/task_students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_task_student(self):
        """Test create task student."""
        response = self.client.post(
            '/api/v1/task_students/',
            {
             TASK: self.task.id,
             STUDENT: self.student.id,
             'solution': 'Solution 1',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_already_exists(self):
        """Test user already exists."""
        response = self.client.post(REGISTER, {USERNAME: 'abc', PASSWORD: '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {ERROR: 'User already exists'})


class StudentModelTest(TestCase):
    """Test Student model."""

    def setUp(self):
        """Set up test data for Student model."""
        self.user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.student = Student.objects.create(
            user=self.user,
            nickname=STUDENT_FIRST,
            registration_date=datetime.date.today(),
        )
        self.task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=self.user)
        self.comment = Comment.objects.create(
            task_id=self.task,
            date_publication=datetime.date.today(),
            text_comment=COMMENT_FIRST,
            student=self.student,
        )
        self.task2 = Task.objects.create(name='Task 2', difficulty=2, user=self.user)
        self.task3 = Task.objects.create(name='Task 3', difficulty=3, user=self.user)
        TaskStudent.objects.create(student=self.student, task=self.task, solution='Solution 1')
        TaskStudent.objects.create(student=self.student, task=self.task2, solution='Solution 2')
        TaskStudent.objects.create(student=self.student, task=self.task3, solution='Solution 3')

    def test_registration_date_in_future_raises_error(self):
        """Test registration date in future raises error."""
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        student = Student(user=self.user, nickname=STUDENT_FIRST, registration_date=future_date)
        with self.assertRaises(ValidationError):
            student.full_clean()

    def test_task_solutions(self):
        """Test task solutions."""
        response = self.client.get(reverse('task_solutions', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rating(self):
        """Test rating."""
        self.assertEqual(self.student.rating, 2)

    def test_validate_difficulty_range_invalid(self):
        """Test validate difficulty range invalid."""
        with self.assertRaises(ValidationError):
            validate_difficulty_range(6)

    def test_max_length_invalid(self):
        """Test max length invalid."""
        with self.assertRaises(ValidationError):
            max_length('a' * status.HTTP_101_SWITCHING_PROTOCOLS)

    def test_str_task(self):
        """Test str task."""
        self.assertEqual(str(self.task), TASK_FIRST)

    def test_str_student(self):
        """Test str student."""
        self.assertEqual(str(self.student), STUDENT_FIRST)

    def test_str_comment(self):
        """Test str comment."""
        self.assertEqual(str(self.comment), f'Comment by Task 1 at {datetime.date.today()}')


class UserRegistrationViewTest(TestCase):
    """Tests user registration view."""

    def setUp(self):
        """Set up test data for user registration view."""
        self.client = Client()

    def test_registration_new_user(self):
        """Test registration new user."""
        response = self.client.post(REGISTER, {USERNAME: TEST_USER, PASSWORD: TEST_PASSWORD})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(username=TEST_USER)
        self.assertIsNotNone(user)
        token = Token.objects.get(user=user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_registration_no_username(self):
        """Test registration no username."""
        response = self.client.post(REGISTER, {PASSWORD: TEST_PASSWORD})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {ERROR: 'Username and password are required'})

    def test_logout_authenticated_user(self):
        """Test logout authenticated user."""
        user = get_user_model().objects.create_user(username=TEST_USER, password=TEST_PASSWORD)
        self.client.force_login(user)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_unauthenticated_user(self):
        """Test logout unauthenticated user."""
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_get_registration(self):
        """Test get registration."""
        response = self.client.get(REGISTER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'register.html')

    def test_create_task_view(self):
        """Test create task view."""
        self.user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('create_task'), data={
            NAME: 'Test Task',
            DESCRIPTION: 'Test Description',
            DIFFICULTY: 1,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Task.objects.count(), initial_task_count + 1)
        response = self.client.get(reverse('tasks_page'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        """Test delete task."""
        user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=user)
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('delete_task', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Task.objects.count(), initial_task_count - 1)

    def test_put_task(self):
        """Test put task."""
        user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=user)
        initial_task_count = Task.objects.count()
        response = self.client.post(reverse('put_task', args=[task.id]), data={
            NAME: 'Test Task',
            DESCRIPTION: 'Test Description',
            DIFFICULTY: 1,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Task.objects.count(), initial_task_count)
        response = self.client.get(reverse('put_task', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment(self):
        """Test create comment."""
        user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=user)
        student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=user)
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse(CREATE_COMMENT, args=[task.id]), data={
            TASK_ID: task.id,
            STUDENT: student.id,
            TEXT_COMMENT: 'Test Comment',
            DATE_PUBLICATION: TEST_DATA,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Comment.objects.count(), initial_comment_count + 1)
        response = self.client.get(reverse(CREATE_COMMENT, args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment(self):
        """Test delete comment."""
        user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=user)
        student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=user)
        comment = Comment.objects.create(
            task_id=task,
            date_publication=TEST_DATA,
            text_comment=COMMENT_FIRST,
            student=student,
        )
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse('delete_comment', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Comment.objects.count(), initial_comment_count - 1)

    def test_put_comment(self):
        """Test put comment."""
        user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.client.login(username=TEST_USER, password=INT_PASSWORD)
        task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=user)
        student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=user)
        comment = Comment.objects.create(
            task_id=task,
            date_publication=TEST_DATA,
            text_comment=COMMENT_FIRST,
            student=student,
        )
        initial_comment_count = Comment.objects.count()
        response = self.client.post(reverse('put_comment', args=[comment.id]), data={
            TASK_ID: task.id,
            STUDENT: student.id,
            TEXT_COMMENT: 'Test Comment',
            DATE_PUBLICATION: TEST_DATA,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Comment.objects.count(), initial_comment_count)
        response = self.client.get(reverse('put_comment', args=[comment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLoginViewTests(TestCase):
    """Tests user login view."""

    def setUp(self):
        """Set up test data for user login view."""
        self.client = Client()
        self.user = User.objects.create_user(username=USER, password=PASS)

    def test_login_no_username_password(self):
        """Test login no username password."""
        response = self.client.post(reverse(LOGIN))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {ERROR: 'Username and password are required'})

    def test_login_no_user(self):
        """Test login no user."""
        response = self.client.post(reverse(LOGIN), {USERNAME: 'wrong', PASSWORD: PASS})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {ERROR: 'User does not exist'})

    def test_login_wrong_password(self):
        """Test login wrong password."""
        response = self.client.post(reverse(LOGIN), {USERNAME: USER, PASSWORD: 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {ERROR: 'Wrong password'})

    def test_login_success(self):
        """Test login success."""
        response = self.client.post(reverse(LOGIN), {USERNAME: USER, PASSWORD: PASS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.json(), {'token': token.key})

    def test_get_login_page(self):
        """Test get login page."""
        response = self.client.get(reverse(LOGIN))
        self.assertTemplateUsed(response, 'login.html')


class UserAdminPermissionTest(TestCase):
    """Tests user admin permission."""

    def setUp(self):
        """Set up test data for user admin permission."""
        self.factory = RequestFactory()
        self.permission = UserAdminPermission()
        self.view = None
        self.user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)

    def test_has_object_permission(self):
        """Test has object permission."""
        request = self.factory.get(MAIN_PAGE)
        request.user = self.user
        objc = None
        self.assertTrue(self.permission.has_object_permission(request, self.view, objc))


class ViewTestCase(TestCase):
    """Tests views."""

    def setUp(self):
        """Set up test data for views."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username=TEST_USER, password=INT_PASSWORD)
        self.task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=self.user)
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.comment = Comment.objects.create(
            task_id=self.task,
            date_publication=TEST_DATA,
            text_comment=COMMENT_FIRST,
            student=self.student,
        )

    def test_tasks_page(self):
        """Test tasks page."""
        request = self.factory.get('/tasks')
        response = tasks_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_page(self):
        """Test task page."""
        request = self.factory.get(f'/task/{self.task.id}')
        response = task_page(request, self.task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_students_page(self):
        """Test students page."""
        request = self.factory.get('/students')
        response = students_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_page(self):
        """Test student page."""
        request = self.factory.get(f'/student/{self.student.id}')
        response = student_page(request, self.student.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comments_page(self):
        """Test comments page."""
        request = self.factory.get('/comments')
        response = comments_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_page(self):
        """Test comment page."""
        request = self.factory.get(f'/comment/{self.comment.id}')
        response = comment_page(request, self.comment.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_main_page(self):
        """Test main page."""
        request = self.factory.get(MAIN_PAGE)
        request.user = AnonymousUser()
        response = main_page(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StudentViewTest(TestCase):
    """Tests student view."""

    def setUp(self):
        """Set up test data for student view."""
        self.client = Client()
        self.user = User.objects.create_user(username=TEST_USER, password=TEST_PASSWORD)
        self.student_data = {NICKNAME: STUDENT_FIRST, REGISTRATION_DATE: TEST_DATA, USER: self.user.id}
        self.student_form = StudentForm(data=self.student_data)

    def test_create_student(self):
        """Test create student."""
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        form = self.student_form
        if form.is_valid():
            response = self.client.post(reverse(CREATE_STUDENT), data=form.cleaned_data)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(response, reverse('students_page'))

    def test_create_student_get_form(self):
        """Test create student get form."""
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.get(reverse(CREATE_STUDENT))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'forms/create_student.html')

    def test_put_student_get_form(self):
        """Test put student get form."""
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.get(reverse('put_student', args=[self.student.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'update/put_student.html')

    def test_create_student_duplicate(self):
        """Test create student duplicate."""
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        response = self.client.post(
            reverse(CREATE_STUDENT),
            data={NICKNAME: STUDENT_FIRST, REGISTRATION_DATE: TEST_DATA, USER: self.user.id},
        )
        self.assertContains(response, 'Вы уже создали студента')

    def test_delete_student(self):
        """Test delete student."""
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        response = self.client.post(reverse('delete_student', args=[self.student.id]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('students_page'))

    def test_put_student(self):
        """Test put student."""
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        form = self.student_form
        if form.is_valid():
            response = self.client.post(reverse('put_student', args=[self.student.id]), data=form.cleaned_data)
            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(response, reverse(STUDENT, args=[self.student.id]))

    def test_create_student_not_authenticated(self):
        """Test create student not authenticated."""
        response = self.client.post(reverse(CREATE_STUDENT), data=self.student_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать студента')

    def test_delete_student_no_permission(self):
        """Test delete student no permission."""
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_student', args=[self.student.id]), follow=True)
        self.assertRedirects(
            response,
            expected_url=reverse(STUDENT, args=[self.student.id]),
            status_code=status.HTTP_302_FOUND, target_status_code=status.HTTP_200_OK,
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого студента')

    def test_put_student_no_permission(self):
        """Test put student no permission."""
        self.student = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user)
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('put_student', args=[self.student.id]), data=self.student_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'У вас нет прав на изменение этого студента')

    def test_unauthenticated_user(self):
        """Test unauthenticated user."""
        response = self.client.get(reverse('create_task'))
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'Вы должны войти в систему, чтобы создать задачу')


class CommentViewTests(TestCase):
    """Tests comment view."""

    def setUp(self):
        """Set up test data for comment view."""
        self.client = Client()
        self.user = User.objects.create_user(username=TEST_USER, password=TEST_PASSWORD)
        self.user1 = User.objects.create_user(username=USER_FIRST, password=PASS)
        self.task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=self.user1)
        self.student1 = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user1)
        self.comment = Comment.objects.create(
            task_id=self.task,
            date_publication=TEST_DATA,
            text_comment=COMMENT_FIRST,
            student=self.student1,
        )

    def test_create_comment_not_authenticated(self):
        """Test create comment not authenticated."""
        response = self.client.post(reverse(CREATE_COMMENT, args=[self.task.id]))
        self.assertContains(response, 'Вы должны войти в систему, чтобы создать комментарий')

    def test_delete_comment_no_permission(self):
        """Test delete comment no permission."""
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_comment', args=[self.comment.id]), follow=True)
        self.assertRedirects(
            response,
            expected_url=reverse(COMMENT, args=[self.comment.id]),
            status_code=status.HTTP_302_FOUND, target_status_code=status.HTTP_200_OK,
        )
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), 'У вас нет прав на удаление этого комментария')

    def test_put_comment_no_permission(self):
        """Test put comment no permission."""
        self.client.login(username=USER_LAST, password=PASS)
        response = self.client.post(reverse('put_comment', args=[self.comment.id]))
        self.assertContains(response, 'У вас нет прав на изменение этого комментария')

    def test_form_no_valid(self):
        """Test form no valid."""
        self.client.login(username=USER_FIRST, password=PASS)
        response = self.client.post(reverse(CREATE_COMMENT, args=[self.task.id]), data={})
        self.assertContains(response, 'Некорректные данные формы')


class CompleteTaskViewTests(TestCase):
    """Tests complete task view."""

    def setUp(self):
        """Set up test data for complete task view."""
        self.client = Client()
        self.user1 = User.objects.create_user(username=USER_FIRST, password=PASS)
        self.user2 = User.objects.create_user(username=USER_LAST, password=PASS)
        self.task = Task.objects.create(name=TASK_FIRST, difficulty=1, user=self.user1)
        self.student1 = Student.objects.create(nickname=STUDENT_FIRST, registration_date=TEST_DATA, user=self.user1)
        self.student2 = Student.objects.create(nickname='Student 2', registration_date=TEST_DATA, user=self.user2)

    def test_complete_task_not_authenticated(self):
        """Test complete task not authenticated."""
        response = self.client.post(reverse(COMPLETE_TASK, args=[self.task.id]))
        self.assertContains(response, 'Вы должны войти в систему и создать студента, чтобы решить задачу')

    def test_completing_a_task_using_an_invalid_form(self):
        """Test completing a task using an invalid form."""
        self.client.login(username=USER_FIRST, password=PASS)
        response = self.client.post(reverse(COMPLETE_TASK, args=[self.task.id]), data={})
        self.assertContains(response, 'Некорректные данные формы. Или вы уже решили эту задачу')

    def test_complete_the_task_in_a_valid_form(self):
        """Test complete the task in a valid form."""
        self.client.login(username=USER_FIRST, password=PASS)
        response = self.client.post(
            reverse(COMPLETE_TASK, args=[self.task.id]),
            data={TASK: self.task.id, STUDENT: self.student1.id, 'solution': 'Solution 1'},
        )
        self.assertRedirects(response, reverse(TASK, args=[self.task.id]))

    def test_completion_task_to_obtain_the_student(self):
        """Test completion task to obtain the student."""
        self.client.login(username=USER_FIRST, password=PASS)
        response = self.client.get(reverse(COMPLETE_TASK, args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Завершить задачу')

    def test_complete_task_no_student_get_request(self):
        """Test complete task no student get request."""
        self.client.login(username=USER_LAST, password=PASS)
        response = self.client.get(reverse(COMPLETE_TASK, args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Завершить задачу')

    def test_completed_task_is_not_authenticated(self):
        """Test completed task is not authenticated."""
        response = self.client.get(reverse(COMPLETE_TASK, args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Завершить задачу')

    def test_delete_task_no_permission(self):
        """Test delete task no permission."""
        self.client.login(username=USER_LAST, password=PASS)
        response = self.client.post(reverse('delete_task', args=[self.task.id]))
        self.assertRedirects(response, reverse(TASK, args=[self.task.id]))

    def test_put_task_no_permission(self):
        """Test put task no permission."""
        self.client.login(username=USER_LAST, password=PASS)
        response = self.client.get(reverse('put_task', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'У вас нет прав на изменение этой задачи')
        self.assertEqual(response.context['form'].instance, self.task)
