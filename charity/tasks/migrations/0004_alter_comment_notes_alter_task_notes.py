# Generated by Django 5.0 on 2023-12-20 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_is_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
