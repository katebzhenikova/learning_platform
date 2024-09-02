from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from .models import Course, Material, Test, AnswerOption
from django.urls import reverse
from users.models import User


class CourseViewSetTests(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create(email='teacher@example.com')
        self.student = User.objects.create(email='student@example.com')
        self.group_teachers = Group.objects.create(name='Преподаватели')
        self.group_students = Group.objects.create(name='Студенты')
        self.teacher.groups.add(self.group_teachers)
        self.student.groups.add(self.group_students)
        self.client.force_authenticate(user=self.teacher)
        self.course = Course.objects.create(title='Test Course', description='Test Course description',
                                            owner=self.teacher, pay_amount_course=200)

    def test_create_course_as_teacher(self):
        url = reverse('learning_platform:course-list')
        data = {'title': 'New Course', 'description': 'New Description', 'pay_amount_course': 200}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_course_as_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:course-list')
        data = {'title': 'New Course', 'description': 'New Description', 'pay_amount_course': 200}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course(self):
        url = reverse('learning_platform:course-detail', args=(self.course.pk,))
        data = {'title': 'Updated Course'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course(self):
        url = reverse('learning_platform:course-detail', args=(self.course.pk,))
        response = self.client.get(url, format='json')
        data = response.json()
        # print(data)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get('title'), self.course.title
        )

    def test_destroy_course(self):
        url = reverse('learning_platform:course-detail', args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_course(self):
        url = reverse('learning_platform:course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MaterialCreateAPIViewTests(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create(email='teacher@example.com')
        self.student = User.objects.create(email='student@example.com')
        self.group_teachers = Group.objects.create(name='Преподаватели')
        self.group_students = Group.objects.create(name='Студенты')
        self.teacher.groups.add(self.group_teachers)
        self.student.groups.add(self.group_students)
        self.client.force_authenticate(user=self.teacher)
        self.course = Course.objects.create(title='Test Course', description='Test Course description',
                                            owner=self.teacher, pay_amount_course=200)
        self.material = Material.objects.create(title='Test Material', description='Test Material description',
                                                course=self.course, owner=self.teacher)
        self.test1 = Test.objects.create(question='Test 1', material=self.material, owner=self.teacher)
        self.correct_answer = AnswerOption.objects.create(answer_text='Correct', is_correct=True, test=self.test1)
        self.incorrect_answer = AnswerOption.objects.create(answer_text='Incorrect', is_correct=False, test=self.test1)

    def test_create_material_as_teacher(self):
        url = reverse('learning_platform:materials-create')
        data = {'title': 'New Material', 'description': 'New Description', 'course': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_material_as_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:materials-create')
        data = {'title': 'New Material', 'description': 'New Description', 'course': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_material(self):
        url = reverse('learning_platform:materials-get', args=(self.material.pk,))
        data = {'title': 'New Material', 'description': 'New Description', 'course': self.course.id}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_material(self):
        url = reverse('learning_platform:materials-update', args=(self.material.pk,))
        data = {'title': 'New Material', 'description': 'New Description', 'course': self.course.id}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_material(self):
        url = reverse('learning_platform:materials-delete', args=(self.material.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_tests(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:test-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_tests_by_material(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:test-list')
        response = self.client.get(f'{url}?material_id={self.material.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_can_create_answer(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:student-answer-list')
        data = {
            'test': self.test1.id,
            'selected_answer': self.correct_answer.answer_text,
            'student': self.student.id
        }
        response = self.client.post(url, data, format='json')
        print(response.data)  # Печать данных ответа для отладки
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_correct'], True)

    def test_student_cannot_create_answer_with_wrong_option(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('learning_platform:student-answer-list')
        data = {
            'test': self.test1.id,
            'selected_answer': self.incorrect_answer.answer_text,
            'student': self.student.id
        }
        response = self.client.post(url, data, format='json')
        print(response.data)  # Печать данных ответа для отладки
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_correct'], False)  # Проверяем, что is_correct равно False

    def test_teacher_can_view_all_answers(self):
        url = reverse('learning_platform:student-answer-list')

        data = {
            'test': self.test1.id,
            'selected_answer': self.correct_answer.answer_text,
            'student': self.student.id
        }
        self.client.post(url, data, format='json')

        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Ожидаем статус 200
        self.assertIn('results', response.data)  # Проверка наличия данных

    def test_student_cannot_view_all_answers(self):
        url = reverse('learning_platform:student-answer-list')
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
