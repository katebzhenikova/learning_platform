from django.contrib.auth.models import AbstractUser
from django.db import models

from config import settings
from learning_platform.models import Course

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="почта пользователя")
    phone = models.CharField(
        max_length=35, verbose_name="телефон пользователя", **NULLABLE
    )
    avatar = models.ImageField(
        upload_to="users/", verbose_name="аватар пользователя", **NULLABLE
    )
    city = models.CharField(max_length=10, verbose_name="город", **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь')
    pay_data = models.DateField(auto_now_add=True, verbose_name='дата оплаты')
    pay_course = models.ForeignKey(Course, verbose_name='оплаченный курс', on_delete=models.CASCADE)
    pay_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='сумма оплаты', **NULLABLE)
    payment_session = models.CharField(max_length=100, verbose_name='id сессии', **NULLABLE)
    payment_link = models.URLField(max_length=400, verbose_name='ссылка на оплату', **NULLABLE)
    payment_status = models.CharField(max_length=50, verbose_name='статус платежа', **NULLABLE)

    def __str__(self):
        return f"Payment {self.id} for Course {self.pay_course.title}"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='курс')
    is_subscribed = models.BooleanField(default=False, verbose_name='подписка')

    def __str__(self):
        return f'{self.user} - {self.course.title}'

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        unique_together = ('user', 'course')

