from django.contrib import admin
from .models import User, SubscriptionPlan, UserSubscription, Consent , PaymentMethod, Payment , Method , UserCard


# Register your models here.

admin.site.register(Consent)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(User)
admin.site.register(Method)
admin.site.register(UserCard)
