from django.contrib import admin
from .models import User, SubscriptionPlan, UserSubscription, Consent , PaymentMethod, Payment , Method , UserCard ,SupportMessage, SupportSession


# Register your models here.

admin.site.register(Consent)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
admin.site.register(User)
admin.site.register(Method)
admin.site.register(UserCard)
admin.site.register(SupportMessage)
admin.site.register(SupportSession)
