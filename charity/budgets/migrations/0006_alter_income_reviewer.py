# Generated by Django 5.0 on 2024-01-12 15:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0005_income_notes_income_reviewer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='reviewer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_incomes', to=settings.AUTH_USER_MODEL),
        ),
    ]
