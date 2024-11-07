from rest_framework import serializers
from .models import User, Consent, SubscriptionPlan, UserSubscription, PaymentMethod, Payment, Method, UserCard, \
    ClientCard, SupportSession, SupportMessage, Advice

import string
import random


class UserRegistrationSerializer(serializers.ModelSerializer):
    website_login = serializers.CharField(read_only=True)
    website_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['telegram_id', 'username', 'website_login', 'website_password']

    def create(self, validated_data):
        user = User.objects.create(
            telegram_id=validated_data['telegram_id'],
            username=validated_data.get('username', '')
        )
        user.website_login = self.generate_random_string(8)
        user.website_password = self.generate_random_string(12)
        user.save()
        return user

    def generate_random_string(self, length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ['id', 'user', 'consent_given', 'consent_date', 'pdf_file']
        read_only_fields = ['user', 'consent_date']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days', 'renewable']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_expiring_soon = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'start_date', 'end_date', 'is_expiring_soon']

    def get_is_expiring_soon(self, obj):
        return obj.is_expiring_soon()


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description']


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])

    class Meta:
        model = Payment
        fields = ['id', 'user', 'subscription_plan', 'payment_method', 'amount', 'transaction_id', 'status',
                  'payment_date']


class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ['id', 'name', 'description', 'details']


class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCard
        fields = ['user', 'card_number', 'card_expiry', 'cardholder_name']


class ClientCardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClientCard
        fields = ['user', 'name', 'age', 'goals', 'challenges', 'created']
        read_only_fields = ['created']


class SupportSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportSession
        fields = ['id', 'user', 'is_active', 'created']


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'session', 'sender', 'message_text', 'timestamp']


class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'title', 'content']


