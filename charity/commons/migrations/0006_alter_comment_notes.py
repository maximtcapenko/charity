# Generated by Django 4.2.9 on 2024-01-31 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commons', '0005_alter_comment_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='notes',
            field=models.TextField(default='test'),
            preserve_default=False,
        ),
    ]
