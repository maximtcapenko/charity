# Generated by Django 5.0 on 2023-12-21 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0001_initial'),
        ('tasks', '0005_alter_task_ward'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='budget',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='budgets.budget'),
        ),
    ]
