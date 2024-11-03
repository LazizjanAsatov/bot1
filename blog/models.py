from django.db import models
from django.utils import timezone


# Create your models here.

class User(models.Model):
    telegram_id = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username if self.username else self.telegram_id


class Consent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rozilik: {self.user.username} - {self.consent_given}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)
        super(UserSubscription, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.plan.name}"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='payments')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)  # To'lov usuli
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20,
                              choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.subscription_plan.name} - {self.payment_method.name} - {self.status}"
