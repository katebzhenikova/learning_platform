from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView, get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from learning_platform.models import AnswerOption, Course, Material, StudentAnswer, Test
from learning_platform.paginators import CustomOffsetPagination, StudentAnswerPagination
from learning_platform.permissions import IsTeacher, IsStudent
from learning_platform.serializers import (
    CourseSerializer,
    MaterialSerializer,
    StudentAnswerSerializer,
    TestSerializer,
    StudentAnswerListSerializer,
)
from rest_framework import serializers
from users.models import Subscription
from learning_platform.tascs import send_update_notification
import logging

logger = logging.getLogger(__name__)


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsTeacher]
        elif self.action in ["update", "retrieve", "destroy"]:
            permission_classes = [IsAuthenticated, IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MaterialCreateAPIView(CreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MaterialListAPIView(ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsStudent | IsTeacher]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            subscribed_courses = Subscription.objects.filter(
                user=user, is_subscribed=True
            ).values_list("course", flat=True)

            return Material.objects.filter(course__in=subscribed_courses).union(
                Material.objects.filter(owner=user)
            )
        else:
            raise PermissionDenied(
                "Authentication is required to access this resource."
            )


class MaterialRetrieveAPIView(RetrieveAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]


class MaterialUpdateAPIView(UpdateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_update(self, serializer):
        updated_material = serializer.save()
        # Найти курс, к которому относится обновленный материал
        course = updated_material.course
        print(f"Обновленный материал: {updated_material}")
        print(f"Курс материала: {course}")

        # Найти все подписки на курс
        subscribers = Subscription.objects.filter(course=course, is_subscribed=True)
        print(f"Найденные подписчики: {subscribers}")
        for subscriber in subscribers:
            print(f"Отправка уведомления для {subscriber.user.email}")
            send_update_notification.delay(
                subscriber.user.email, updated_material.title
            )


class MaterialDestroyAPIView(DestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    pagination_class = CustomOffsetPagination

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Преподаватели могут создавать, изменять и удалять тесты
            permission_classes = [IsTeacher]
        elif self.action == "list":
            # Студенты и преподаватели могут просматривать тесты
            permission_classes = [IsStudent | IsTeacher]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.is_authenticated:
            if user.groups.filter(name="Преподаватели").exists():
                queryset = queryset.filter(material__owner=user)

            else:  # Студенты
                # Получаем список материалов, на которые студент подписан
                subscribed_courses = Subscription.objects.filter(
                    user=user, is_subscribed=True
                ).values_list("course", flat=True)
                material_ids = Material.objects.filter(
                    course__in=subscribed_courses
                ).values_list("id", flat=True)

                # Фильтруем тесты по материалам, на которые студент подписан
                queryset = queryset.filter(material__id__in=material_ids)

        # Фильтрация по материалу через запрос
        material_id = self.request.query_params.get("material_id")
        if material_id:
            queryset = queryset.filter(material__id=material_id)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StudentAnswerViewSet(viewsets.ModelViewSet):
    """Класс ответов студентов на тесты"""

    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer
    pagination_class = StudentAnswerPagination

    def get_permissions(self):
        """Разрешения пользователей"""
        if self.request.method == "POST":
            # Студенты могут создавать ответы
            return [IsStudent()]
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            # Преподаватели могут изменять и удалять ответы
            return [IsTeacher()]
        # Преподаватели могут просматривать все ответы, студенты только свои
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Создание студентом ответов на тесты"""
        selected_answer_text = self.request.data.get("selected_answer")
        test = serializer.validated_data["test"]
        correct_answer = AnswerOption.objects.filter(test=test, is_correct=True).first()
        is_correct = (
            correct_answer and correct_answer.answer_text == selected_answer_text
        )
        serializer.save(student=self.request.user, is_correct=is_correct)


class CheckAnswersView(APIView):
    """Проверка ответов студентов на тесты"""

    def get_permissions(self):
        """Определение разрешений для просмотра ответов"""
        if self.request.user.groups.filter(name="Студенты").exists():
            return [IsAuthenticated(), IsStudent()]
        elif self.request.user.groups.filter(name="Преподаватели").exists():
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated()]  # По умолчанию доступен для аутентифицированных пользователей

    def get(self, request, *args, **kwargs):
        material_id = request.query_params.get("material_id")
        if not material_id:
            return Response(
                {"detail": "material_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем все тесты, связанные с данным материалом
        material = get_object_or_404(Material, id=material_id)
        tests = Test.objects.filter(material=material)
        test_ids = tests.values_list('id', flat=True)

        # Проверяем роль пользователя и получаем ответы
        if request.user.groups.filter(name="Студенты").exists():
            # Студенты могут видеть только свои ответы
            answers = StudentAnswer.objects.filter(student=request.user, test_id__in=test_ids)
        elif request.user.groups.filter(name="Преподаватели").exists():
            # Преподаватели могут видеть ответы студентов по материалу
            answers = StudentAnswer.objects.filter(test_id__in=test_ids)
        else:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Сериализуем ответы
        serializer = StudentAnswerSerializer(answers, many=True)

        return Response(serializer.data)