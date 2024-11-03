from django.urls import path
from .views import UserRegistrationView, ConsentView, SubscriptionPlanListView, SubscribeView, SubscriptionStatusView, \
    PaymentMethodListView, MakePaymentView, PaymentStatusView, ConsentStatusView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(),name='register'),
    path('consent/<str:telegram_id>/', ConsentView.as_view(), name='consent'),
    path('consent-status/<str:telegram_id>/', ConsentStatusView.as_view(), name='consent-status'),
    path('subscription-plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('subscribe/<str:telegram_id>/', SubscribeView.as_view(), name='subscribe'),
    path('subscription-status/<str:telegram_id>/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment-methods'),
    path('make-payment/<str:telegram_id>/', MakePaymentView.as_view(), name='make-payment'),
    path('payment-status/<str:transaction_id>/', PaymentStatusView.as_view(), name='payment-status'),
]