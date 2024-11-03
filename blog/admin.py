from django.contrib import admin
from .models import User, SubscriptionPlan, UserSubscription, Consent , PaymentMethod, Payment


# Register your models here.

admin.site.register(Consent)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(User)
