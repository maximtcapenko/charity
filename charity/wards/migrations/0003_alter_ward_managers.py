# Generated by Django 4.2.9 on 2024-01-27 23:35

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('wards', '0002_alter_ward_options'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='ward',
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]