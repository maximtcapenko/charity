# Generated by Django 5.0 on 2024-01-08 23:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0002_alter_budget_options_alter_income_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='reviewers',
            field=models.ManyToManyField(related_name='budget_reviewers', to=settings.AUTH_USER_MODEL),
        ),
    ]