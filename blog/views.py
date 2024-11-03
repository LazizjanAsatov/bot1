from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, SubscriptionPlan, UserSubscription, Payment, PaymentMethod, Consent
from .serializers import UserRegistrationSerializer, ConsentSerializer, UserSubscriptionSerializer, \
    SubscriptionPlanSerializer, PaymentSerializer, PaymentMethodSerializer


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user, created = User.objects.get_or_create(
                telegram_id=serializer.validated_data['telegram_id'],
                defaults={'username': serializer.validated_data.get('username', '')}
            )
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response({'message': 'Foydalanuvchi muvaffaqiyatli ro\'yxatdan o\'tdi.'}, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConsentView(APIView):
    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        consent_given = request.data.get('consent_given', False)

        consent, created = Consent.objects.update_or_create(
            user=user,
            defaults={
                'consent_given': consent_given,
                'consent_date': timezone.now() if consent_given else None
            }
        )

        return Response({'message': 'Rozilik holati muvaffaqiyatli saqlandi.'}, status=status.HTTP_200_OK)

class ConsentStatusView(APIView):
    def get(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            consent = Consent.objects.get(user=user)
            return Response({
                'consent_given': consent.consent_given,
                'consent_date': consent.consent_date
            }, status=status.HTTP_200_OK)
        except Consent.DoesNotExist:
            return Response({'consent_given': False, 'consent_date': None}, status=status.HTTP_200_OK)



class SubscriptionPlanListView(APIView):
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'Obuna turi ID sini kiriting.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Obuna turi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        user_subscription = UserSubscription.objects.create(user=user, plan=plan)
        serializer = UserSubscriptionSerializer(user_subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubscriptionStatusView(APIView):
    def get(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        user_subscription = UserSubscription.objects.filter(user=user).order_by('-end_date').first()
        if user_subscription and user_subscription.end_date > timezone.now():
            serializer = UserSubscriptionSerializer(user_subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'Foydalanuvchi obuna emas yoki obuna muddati tugagan.'}, status=status.HTTP_200_OK)


class MakePaymentView(APIView):
    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        plan_id = request.data.get('subscription_plan')
        method_id = request.data.get('payment_method')
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({'error': 'Tranzaksiya ID sini kiriting.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Obuna turi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment_method = PaymentMethod.objects.get(id=method_id)
        except PaymentMethod.DoesNotExist:
            return Response({'error': 'To\'lov usuli topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        amount = subscription_plan.price

        payment = Payment.objects.create(
            user=user,
            subscription_plan=subscription_plan,
            payment_method=payment_method,
            amount=amount,
            transaction_id=transaction_id,
            status='pending'
        )
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    def get(self, request, transaction_id):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Tranzaksiya topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentMethodListView(APIView):
    def get(self, request):
        methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
