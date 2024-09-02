import os

from django.core.management import BaseCommand
from dotenv import load_dotenv

from config.settings import BASE_DIR
from users.models import User

load_dotenv(BASE_DIR / ".env")


class Command(BaseCommand):
    """Создаем суперюзера и командой python manage.py auth записываем данные в БД"""

    def handle(self, *args, **options):
        user = User.objects.create(
            email=os.getenv("SUPER_USER_EMAIL"),
            first_name="Admin",
            last_name="learning_platform",
            is_staff=True,
            is_superuser=True,
            phone=None,
        )

        user.set_password(os.getenv("SUPER_USER_EMAIL_PASS"))
        user.save()
