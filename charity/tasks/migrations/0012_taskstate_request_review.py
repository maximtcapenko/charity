# Generated by Django 5.0 on 2024-01-21 21:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0004_alter_approvement_options_requestreview'),
        ('tasks', '0011_task_comments_taskstate_comments_delete_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskstate',
            name='request_review',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='funds.requestreview'),
        ),
    ]
