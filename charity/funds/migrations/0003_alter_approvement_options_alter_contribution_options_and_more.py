# Generated by Django 5.0 on 2024-01-08 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0002_contributor_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approvement',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='contribution',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='contributor',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='fund',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='volunteerprofile',
            options={'ordering': ['-date_created']},
        ),
    ]