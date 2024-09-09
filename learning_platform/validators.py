import re
from rest_framework.exceptions import ValidationError


class NoExternalLinksValidator:
    def __call__(self, value):
        # Регулярное выражение для поиска всех ссылок в тексте
        url_pattern = re.compile(r'(https?://[^\s]+)')
        urls = url_pattern.findall(value)

        # Проверяем каждую ссылку
        for url in urls:
            if 'youtube.com' not in url:
                raise ValidationError('Материалы не должны содержать ссылки на сторонние ресурсы, кроме youtube.com.')

        return value

