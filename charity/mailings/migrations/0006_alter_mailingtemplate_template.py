# Generated by Django 4.2.10 on 2024-02-12 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0005_remove_mailingtemplate_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailingtemplate',
            name='template',
            field=models.TextField(),
        ),
    ]