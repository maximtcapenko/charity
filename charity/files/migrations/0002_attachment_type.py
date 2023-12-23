# Generated by Django 5.0 on 2023-12-19 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='type',
            field=models.CharField(choices=[('IMG', 'Image'), ('PDF', 'Pdf'), ('DOC', 'Word'), ('EXCEL', 'Excel'), ('VIDEO', 'Video')], default=False, max_length=6),
            preserve_default=False,
        ),
    ]
