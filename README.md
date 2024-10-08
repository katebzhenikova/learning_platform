ПРОЕКТ САМООБУЧЕНИЯ

Этот проект представляет собой приложение на Django с использованием Django REST Framework (DRF), 
Оно включает несколько сервисов, таких как Django, PostgreSQL, 
Redis и Celery, Stripe

Содержание

Структура проекта
Проект имеет следующую структуру:

learning_platform/
│─ config                  # Настройки проекта
│─ learning_platform       # Основное приложение
│─ users                   # Приложение для управления пользователями
│─ requirements.txt       # Зависимости Python
│─ ...                    # Другие файлы, связанные с Django
│─ .env                   # Файл с переменными окружения
└─ README.md              # Описание проекта

Сервисы

1. Django: Основное веб-приложение.
2. PostgreSQL: Реляционная база данных.
3. Redis: Хранилище структур данных в памяти, используемое в качестве брокера сообщений для Celery.
4. Celery: Асинхронная очередь задач.
5. Stripe: Платформа для обработки онлайн-платежей

Переменные окружения
Проект использует файл .env для управления переменными окружения. 
Этот файл должен находиться в корневой директории проекта.

Запуск проекта
1. Django: Запустите сервер Django командой:
python manage.py runserver
Проект будет доступен по адресу http://127.0.0.1:8000/.

2. PostgreSQL: Загрузите фикстуры данных:

python3 manage.py loaddata learning_platform.json
python3 manage.py loaddata users.json

3. Redis: Установите Redis и запустите его:

pip install redis
Запустите Redis из командной строки:
C:\Redis> redis-server.exe

4. Celery: Установите Celery и дополнительные зависимости:

pip install celery
pip install eventlet
pip install django-celery-beat
Запустите рабочие процессы Celery:

celery -A config worker -l INFO -P eventlet

Задачи в фоновом режиме
Функция send_update_notification предназначена для отправки 
уведомлений по электронной почте об обновлениях материалов курса. 
Функция запускается асинхронно через Celery.

Сохранение результатов проверки покрытия тестами.

pip install coverage 
coverage run manage.py test 
coverage report -m > coverage_report.txt

=========================================================

Логика проекта
Доступ к курсам:
Пользователь, который не зарегистрирован или не авторизован, может просматривать список курсов с их описанием.

Доступ к обучающим материалам и тестам:
Для получения доступа ко всем обучающим материалам и тестам пользователь должен зарегистрироваться и оплатить подписку 
на платформу.
После успешной оплаты и активации подписки пользователь сможет полноценно использовать все материалы и тесты.

Оповещения:
Когда обучающие материалы обновляются, студенты, подписанные на обновления, получают уведомление на электронную почту.

Роли и разрешения:
Суперпользователь: Имеет полный доступ ко всем функциям платформы.
Преподаватели: Могут создавать и управлять материалами и тестами. Для доступа к созданию и редактированию материалов и 
тестов используется разрешение IsTeacher, проверяющее, что текущий пользователь является владельцем объекта.
Студенты: Могут просматривать материалы и проходить тесты. Проверка доступа осуществляется с помощью разрешения 
IsStudent, которое проверяет, что пользователь состоит в группе "Студенты".

Разрешения:
IsTeacher: Проверяет, что текущий пользователь является владельцем объекта.
IsStudent: Проверяет, что текущий пользователь состоит в группе "Студенты".


Эндпойнты:
learning_platform:
GET http://localhost:8000/learning_platform/course/ - Получить список всех курсов
POST http://localhost:8000/learning_platform/course/ - Создать новый курс
PUT http://localhost:8000/learning_platform/course/{id}/ - Обновить информацию о конкретном курсе по его ID
PATCH http://localhost:8000/learning_platform/course/{id}/ - Частично обновить информацию о конкретном курсе по его ID
DELETE http://localhost:8000/learning_platform/course/{id}/ - Удалить конкретный курс по его ID

GET http://localhost:8000/learning_platform/materials/ - Получить список всех обучающих материалов
POST http://localhost:8000/learning_platform/materials/create/ - Создать новый обучающий материал
GET http://localhost:8000/learning_platform/materials/{id}/ - Получить информацию о конкретном материале по его ID
PUT http://localhost:8000/learning_platform/materials/{id}/ - Обновить информацию о конкретном материале по его ID
PATCH http://localhost:8000/learning_platform/materials/{id}/ - Частично обновить информацию о конкретном материале по его ID
DELETE http://localhost:8000/learning_platform/materials/{id}/ - Удалить конкретный материал по его ID

GET http://localhost:8000/learning_platform/tests/?material_id={id} - Получить тесты на обучающие материалы
POST http://localhost:8000/learning_platform/student_answers/ - Отправить ответ на тест
GET http://localhost:8000/learning_platform/check-answers/?material_id={id} - Получить ответы студента

users:
GET http://localhost:8000/users/payment/ - Получить список всех платежей
POST http://localhost:8000/users/payment/create/ - Создать новый платеж
GET http://localhost:8000/users/payment/status/<payment_id>/ - Получить статус платежа по его ID
POST http://localhost:8000/users/subscription/update/<int:payment_id>/ - Получить подписку по ID оплаты
POST http://localhost:8000/users/register/ - Регистрация нового пользователя
POST http://localhost:8000/users/token/ - Получает JWT токен для аутентификации
POST http://localhost:8000/users/token/refresh/ - Обновляет JWT токен

Документация:
http://127.0.0.1:8000/swagger/
Django administration:
http://127.0.0.1:8000/admin/

