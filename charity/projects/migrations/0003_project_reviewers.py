# Generated by Django 5.0 on 2024-01-08 23:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='reviewers',
            field=models.ManyToManyField(related_name='project_reviewers', to=settings.AUTH_USER_MODEL),
        ),
    ]
