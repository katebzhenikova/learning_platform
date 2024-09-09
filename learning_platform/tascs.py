from celery import shared_task
from django.core.mail import send_mail
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


@shared_task
def send_update_notification(email, course_title):
    """Отправка на почту сообщения об обновлении курса"""
    subject = f"Обновление курса: {course_title}"
    message = f'Уважаемый пользователь,\n\nКурс "{course_title}" был обновлен. Пожалуйста, проверьте новые материалы.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
