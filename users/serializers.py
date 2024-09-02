from rest_framework import serializers
from django.contrib.auth.models import Group

from learning_platform.serializers import CourseSerializer
from users.models import Payment, User, Subscription


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'user', 'pay_course', 'payment_session', 'payment_link', 'payment_status']
        extra_kwargs = {
            'user': {'required': False},
            'pay_course': {'required': True},
            'pay_amount': {'required': True}
        }


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')
    groups = serializers.SlugRelatedField(slug_field='name', queryset=Group.objects.all(), many=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'is_active', 'groups', 'payments']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        instance.groups.set(groups)
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'course', 'is_subscribed']





