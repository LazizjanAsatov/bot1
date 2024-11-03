from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, SubscriptionPlan, UserSubscription, Payment, PaymentMethod, Consent, Method, SupportSession, \
    SupportMessage
from .serializers import UserRegistrationSerializer, ConsentSerializer, UserSubscriptionSerializer, \
    SubscriptionPlanSerializer, PaymentSerializer, PaymentMethodSerializer, MethodSerializer, UserCardSerializer


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


class MethodsListView(APIView):
    def get(self, request):
        methods = Method.objects.all()
        serializer = MethodSerializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MethodDetailView(APIView):
    def get(self, request, method_id):
        try:
            method = Method.objects.get(id=method_id)
            serializer = MethodSerializer(method)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Method.DoesNotExist:
            return Response({'error': 'Metod topilmadi.'}, status=status.HTTP_404_NOT_FOUND)


class StatisticsView(APIView):
    def get(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        statistics = {
            "total_subscriptions": UserSubscription.objects.filter(user=user).count(),
            "total_payments": Payment.objects.filter(user=user, status='completed').count(),
            "last_subscription": UserSubscription.objects.filter(user=user).order_by('-end_date').first(),
        }
        return Response(statistics, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        profile_data = {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "created": user.created,
            "current_subscription": UserSubscription.objects.filter(user=user, end_date__gte=timezone.now()).first(),
            "total_payments": Payment.objects.filter(user=user, status='completed').count(),
        }
        return Response(profile_data, status=status.HTTP_200_OK)


class UserCardView(APIView):
    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        card_data = {
            "user": user.id,
            "card_number": request.data.get("card_number"),
            "card_expiry": request.data.get("card_expiry"),
            "cardholder_name": request.data.get("cardholder_name"),
        }
        serializer = UserCardSerializer(data=card_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StartSupportSessionView(APIView):
    def post(self, request, telegram_id):
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'error': 'Foydalanuvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        session, created = SupportSession.objects.get_or_create(user=user, is_active=True)
        return Response({
            'session_id': session.id,
            'message': 'Support sessiyasi boshlandi.',
        }, status=status.HTTP_200_OK)


import requests

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
MANAGER_CHAT_ID = 'MANAGER_CHAT_ID'


def send_telegram_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()


class SendSupportMessageView(APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        sender = request.data.get("sender")  # 'user' yoki 'manager'
        message_text = request.data.get("message_text")

        try:
            session = SupportSession.objects.get(id=session_id, is_active=True)
        except SupportSession.DoesNotExist:
            return Response({'error': 'Sessiya topilmadi yoki yakunlangan.'}, status=status.HTTP_404_NOT_FOUND)

        message = SupportMessage.objects.create(
            session=session,
            sender=sender,
            message_text=message_text
        )

        if sender == "user":
            response = send_telegram_message(MANAGER_CHAT_ID,
                                             f"User {session.user.username or session.user.telegram_id}: {message_text}")
            if not response.get("ok"):
                return Response({'error': 'Menejerga xabar yuborishda xatolik yuz berdi.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif sender == "manager":
            user_chat_id = session.user.telegram_id
            response = send_telegram_message(user_chat_id, f"Manager: {message_text}")
            if not response.get("ok"):
                return Response({'error': 'Foydalanuvchiga xabar yuborishda xatolik yuz berdi.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Xabar yuborildi.'}, status=status.HTTP_201_CREATED)


class GetSupportMessagesView(APIView):
    def get(self, request, session_id):
        try:
            session = SupportSession.objects.get(id=session_id)
        except SupportSession.DoesNotExist:
            return Response({'error': 'Sessiya topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        messages = SupportMessage.objects.filter(session=session).order_by('timestamp')
        message_data = [
            {
                'sender': msg.sender,
                'message_text': msg.message_text,
                'timestamp': msg.timestamp
            }
            for msg in messages
        ]
        return Response({'messages': message_data}, status=status.HTTP_200_OK)
