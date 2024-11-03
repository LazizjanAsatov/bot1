from rest_framework import serializers
from .models import User, Consent, SubscriptionPlan, UserSubscription, PaymentMethod, Payment, Method, UserCard


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['telegram_id', 'username']


class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ['user', 'consent_given', 'consent_date']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'description', 'price', 'duration_days']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'start_date', 'end_date']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description']


class PaymentSerializer(serializers.ModelSerializer):
    payment_method = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['user', 'subscription_plan', 'payment_method', 'amount', 'transaction_id', 'status', 'payment_date']

class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ['id', 'name', 'description', 'details']

class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCard
        fields = ['user', 'card_number', 'card_expiry', 'cardholder_name']

