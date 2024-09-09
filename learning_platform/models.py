from django.db import models
from config import settings

NULLABLE = {"null": True, "blank": True}


class Course(models.Model):
    title = models.CharField(max_length=150, verbose_name="название курса")
    description = models.TextField(max_length=500, verbose_name="описание курса")
    preview = models.ImageField(
        upload_to="photo_course/", verbose_name="превью", **NULLABLE
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        verbose_name="владелец",
    )
    pay_amount_course = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="стоимость курса"
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "курс"
        verbose_name_plural = "курсы"


class Material(models.Model):
    title = models.CharField(max_length=150, verbose_name="название")
    description = models.TextField(max_length=1000, verbose_name="описание")
    course = models.ForeignKey(
        Course, related_name="material", on_delete=models.CASCADE
    )
    video_url = models.URLField(verbose_name="ссылка на видео", **NULLABLE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        verbose_name="владелец",
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Обучающий материал"
        verbose_name_plural = "Обучающие материалы"


class Test(models.Model):
    question = models.CharField(max_length=255, verbose_name="вопрос")
    material = models.ForeignKey(
        Material,
        related_name="tests",
        on_delete=models.CASCADE,
        verbose_name="обучающий материал",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        verbose_name="владелец",
    )

    def __str__(self):
        return f"{self.question}"

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class AnswerOption(models.Model):
    test = models.ForeignKey(
        Test, related_name="answer_options", on_delete=models.CASCADE
    )
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        **NULLABLE,
        verbose_name="владелец",
    )

    def __str__(self):
        return f"{self.test}"

    class Meta:
        verbose_name = "Ответы на тест"
        verbose_name_plural = "Ответы на тесты"


class StudentAnswer(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.is_correct}"

    class Meta:
        verbose_name = "Ответы студента"
        verbose_name_plural = "Ответы студента"
