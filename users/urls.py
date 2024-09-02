from django.urls import path
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.apps import UsersConfig
from users.views import PaymentListAPIView, UserCreateAPIView, PaymentCreateAPIView, PaymentStatusAPIView, \
    SubscriptionHandlerAPIView

app_name = UsersConfig.name

urlpatterns = [

    path('payment/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payment/status/<int:payment_id>/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('subscription/update/<int:payment_id>/', SubscriptionHandlerAPIView.as_view(), name='subscription-handler'),

    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),

]


