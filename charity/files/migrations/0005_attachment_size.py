# Generated by Django 4.2.15 on 2024-09-02 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0004_attachment_storage_provider_alter_attachment_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='size',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]