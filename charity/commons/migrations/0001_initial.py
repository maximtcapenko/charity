# Generated by Django 5.0 on 2024-01-11 22:10

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField()),
                ('message', models.TextField()),
                ('is_viewed', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
            },
        ),
    ]
