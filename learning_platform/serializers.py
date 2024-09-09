from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from learning_platform.models import AnswerOption, Course, Material, StudentAnswer, Test
from learning_platform.validators import NoExternalLinksValidator


class CourseSerializer(ModelSerializer):
    title = serializers.CharField(validators=[NoExternalLinksValidator()])
    preview = serializers.URLField(validators=[NoExternalLinksValidator()], required=False, allow_blank=True)

    class Meta:
        model = Course
        fields = "__all__"


class MaterialSerializer(ModelSerializer):

    class Meta:
        model = Material
        fields = "__all__"


class AnswerOptionSerializer(ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ["id", "answer_text"]


class TestSerializer(ModelSerializer):
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ["id", "question", "answer_options"]


class StudentAnswerListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        student_answers = [StudentAnswer(**item) for item in validated_data]
        return StudentAnswer.objects.bulk_create(student_answers)


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ["id", "student", "test", "selected_answer", "is_correct", "timestamp"]
        read_only_fields = ["student", "is_correct"]
        list_serializer_class = StudentAnswerListSerializer
