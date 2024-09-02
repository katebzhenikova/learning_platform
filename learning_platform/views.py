from rest_framework import permissions, status, viewsets
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from learning_platform.models import (AnswerOption, Course, Material,
                                      StudentAnswer, Test)
from learning_platform.paginators import CustomOffsetPagination, StudentAnswerPagination
from learning_platform.permissions import IsTeacher, IsStudent
from learning_platform.serializers import (CourseSerializer,
                                           MaterialSerializer,
                                           StudentAnswerSerializer,
                                           TestSerializer)
from users.models import Subscription
from learning_platform.tascs import send_update_notification


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated, IsTeacher]
        elif self.action in ["update", "retrieve", "destroy"]:
            permission_classes = [IsAuthenticated, IsTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class MaterialCreateAPIView(CreateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MaterialListAPIView(ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]


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
        print(f'Обновленный материал: {updated_material}')
        print(f'Курс материала: {course}')

        # Найти все подписки на курс
        subscribers = Subscription.objects.filter(course=course, is_subscribed=True)
        print(f'Найденные подписчики: {subscribers}')
        for subscriber in subscribers:
            print(f'Отправка уведомления для {subscriber.user.email}')
            send_update_notification.delay(subscriber.user.email, updated_material.title)


class MaterialDestroyAPIView(DestroyAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsTeacher]


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    pagination_class = CustomOffsetPagination

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Преподаватели могут создавать, изменять и удалять тесты
            return [IsTeacher()]
        # Студенты могут только просматривать тесты
        return [IsStudent()]

    def get_queryset(self):
        material_id = self.request.query_params.get('material_id')
        if material_id:
            return self.queryset.filter(material_id=material_id)
        return self.queryset.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.all().order_by('id')  # Явный порядок
    serializer_class = StudentAnswerSerializer
    pagination_class = StudentAnswerPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            # Студенты могут создавать ответы
            return [IsStudent()]
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Преподаватели могут изменять и удалять ответы
            return [IsTeacher()]
        # Преподаватели могут просматривать все ответы, студенты только свои
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        selected_answer_text = self.request.data.get('selected_answer')
        test = serializer.validated_data['test']
        correct_answer = AnswerOption.objects.filter(test=test, is_correct=True).first()
        is_correct = correct_answer and correct_answer.answer_text == selected_answer_text
        serializer.save(is_correct=is_correct)



