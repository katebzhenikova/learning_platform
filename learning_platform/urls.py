from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter

from learning_platform.apps import LearningPlatformConfig
from learning_platform.views import (CourseViewSet,
                                     MaterialCreateAPIView,
                                     MaterialDestroyAPIView,
                                     MaterialListAPIView,
                                     MaterialRetrieveAPIView,
                                     MaterialUpdateAPIView, TestViewSet, StudentAnswerViewSet, )

app_name = LearningPlatformConfig.name

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')
router.register(r'tests', TestViewSet, basename='test')
router.register(r'student_answers', StudentAnswerViewSet, basename='student-answer')

urlpatterns = [
    path("materials/", MaterialListAPIView.as_view(), name="materials-list"),
    path("materials/create/", MaterialCreateAPIView.as_view(), name="materials-create"),
    path(
        "materials/<int:pk>/", MaterialRetrieveAPIView.as_view(), name="materials-get"
    ),
    path(
        "materials/update/<int:pk>/",
        MaterialUpdateAPIView.as_view(),
        name="materials-update",
    ),
    path(
        "materials/delete/<int:pk>",
        MaterialDestroyAPIView.as_view(),
        name="materials-delete",
    ),

]

urlpatterns += router.urls
