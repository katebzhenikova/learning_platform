import stripe
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import generics, status
from rest_framework.views import APIView

from learning_platform.permissions import IsTeacher, IsStudent
from users.models import Payment, User, Subscription
from users.serializers import PaymentSerializer, UserSerializer
from users.services import create_stripe_price, create_stripe_session, create_stripe_product


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('pay_course', 'user')
    orderind_fields = ('pay_data',)
    permission_classes = [IsAuthenticated, IsStudent]


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('pay_course', 'user')
    orderind_fields = ('pay_data',)
    permission_classes = [IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        if payment.pay_course:
            amount = payment.pay_course.pay_amount_course
            payment.pay_amount = amount
            product_name = payment.pay_course.title
            product = create_stripe_product(product_name)
            price = create_stripe_price(amount, product)
            # Создаем сессию оплаты в Stripe
            session = create_stripe_session(price)
            # Сохраняем данные о сессии и ссылке на оплату в платеже
            payment.payment_session = session['id']
            payment.payment_link = session['url']
            payment.save()
            return Response({
                "payment_id": payment.id,
                "payment_link": payment.payment_link
            })


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = get_object_or_404(Payment, id=payment_id)
            session_id = payment.payment_session

            session = stripe.checkout.Session.retrieve(session_id)
            payment_intent_id = session.payment_intent
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            payment.payment_status = payment_intent.status
            payment.save()

            response_data = {
                'status': payment_intent.status,
                'amount_received': payment_intent.amount_received / 100,
                'currency': payment_intent.currency
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except stripe.error.InvalidRequestError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class SubscriptionHandlerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            if payment.payment_status == 'succeeded':
                subscription = Subscription.objects.filter(user=payment.user, course=payment.pay_course).first()
                if subscription:
                    subscription.is_subscribed = True
                    subscription.save()
                else:
                    Subscription.objects.create(user=payment.user, course=payment.pay_course, is_subscribed=True)

                return Response({'subscription_status': 'Subscription successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment not successful'}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



