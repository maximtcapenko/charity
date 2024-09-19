# Generated by Django 3.2 on 2021-05-10 13:05

from django.db import migrations

import eav.fields


class Migration(migrations.Migration):
    dependencies = [
        ('eav', '0004_alter_value_value_bool'),
    ]

    operations = [
        migrations.AddField(
            model_name='value',
            name='value_csv',
            field=eav.fields.CSVField(blank=True, default="", null=True),
        ),
        migrations.AlterField(
            model_name='attribute',
            name='datatype',
            field=eav.fields.EavDatatypeField(
                choices=[
                    ('text', 'Text'),
                    ('date', 'Date'),
                    ('float', 'Float'),
                    ('int', 'Integer'),
                    ('bool', 'True / False'),
                    ('object', 'Django Object'),
                    ('enum', 'Multiple Choice'),
                    ('json', 'JSON Object'),
                    ('csv', 'Comma-Separated-Value'),
                ],
                max_length=6,
                verbose_name='Data Type',
            ),
        ),
    ]