# Generated by Django 4.2.9 on 2024-02-04 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_alter_task_comments_alter_taskstate_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='actual_expense_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
