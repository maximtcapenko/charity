# Generated by Django 5.0 on 2024-01-12 15:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_task_reviewer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='reviewer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_expenses', to=settings.AUTH_USER_MODEL),
        ),
    ]