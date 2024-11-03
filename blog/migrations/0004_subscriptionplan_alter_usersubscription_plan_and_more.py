# Generated by Django 5.1.2 on 2024-11-03 14:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_subscription_usersubscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration_days', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.subscriptionplan'),
        ),
        migrations.DeleteModel(
            name='Subscription',
        ),
    ]