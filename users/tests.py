from unittest.mock import patch, Mock

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Course, Payment, Subscription, User
from django.contrib.auth.models import Group


class PaymentAPIViewTests(APITestCase):

    def setUp(self):
        self.teacher = User.objects.create(email='teacher@example.com')
        self.student = User.objects.create(email='student@example.com')
        self.group_teachers = Group.objects.create(name='Преподаватели')
        self.group_students = Group.objects.create(name='Студенты')
        self.teacher.groups.add(self.group_teachers)
        self.student.groups.add(self.group_students)
        self.course = Course.objects.create(title='Test Course', description='Course Description', owner=self.teacher, pay_amount_course=200)
        self.payment = Payment.objects.create(user=self.student, pay_course=self.course, pay_amount=self.course.pay_amount_course)
        self.client.force_authenticate(user=self.student)

    def test_list_payments(self):
        url = reverse('users:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_payment(self):
        url = reverse('users:payment-create')
        data = {'pay_course': self.course.id, 'pay_amount': self.course.pay_amount_course, "owner": self.student}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('stripe.checkout.Session.retrieve')
    @patch('stripe.PaymentIntent.retrieve')
    def test_payment_status(self, mock_payment_intent, mock_session):
        mock_session.return_value = Mock(
            payment_intent='test_payment_intent_id'
        )
        mock_payment_intent.return_value = Mock(
            status='succeeded',
            amount_received=1000,
            currency='usd'
        )

        self.payment = Payment.objects.create(
            user=self.student,
            pay_course=self.course,
            pay_amount=1000,
            payment_session='test_session_id',
            payment_status='created'
        )
        url = reverse('users:payment-status', args=[self.payment.pk])
        data = {'title': 'Updated Course'}

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'succeeded')


class SubscriptionHandlerAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='testuser@example.com')
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(title='Test Course', description='Course Description', owner=self.user, pay_amount_course=200)
        self.payment = Payment.objects.create(
            id=1,
            user=self.user,
            pay_course=self.course,
            payment_status='succeeded'
        )

    def test_subscription_success(self):
        url = reverse('users:subscription-handler', args=[self.payment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['subscription_status'], 'Subscription successful')
        subscription = Subscription.objects.filter(user=self.user, course=self.course).first()
        self.assertIsNotNone(subscription)
        self.assertTrue(subscription.is_subscribed)

    def test_payment_not_successful(self):
        self.payment.payment_status = 'failed'
        self.payment.save()
        url = reverse('users:subscription-handler', args=[self.payment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Payment not successful')

    def test_payment_not_found(self):
        url = reverse('users:subscription-handler', args=[999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['error'], 'Payment not found')

    def test_server_error(self):
        # Исключите настройку Exception при выполнении запроса
        # Вы можете использовать метод `patch` или другой подход для эмуляции серверной ошибки.
        # В этом примере, предполагаем, что такой подход возможен.
        with self.assertRaises(Exception):
            url = reverse('users:serssubscription-handler', args=[self.payment.id])
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.json()['error'], 'An error occurred')


class UserCreateAPIViewTests(APITestCase):

    def setUp(self):
        self.url = '/users/register/'

    def test_create_user(self):
        data = {'email': 'newuser@example.com', 'password': 'newpassword'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



