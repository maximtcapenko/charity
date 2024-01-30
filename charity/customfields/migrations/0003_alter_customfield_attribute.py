# Generated by Django 4.2.9 on 2024-01-28 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eav', '0011_alter_attribute_id_alter_enumgroup_id_and_more'),
        ('customfields', '0002_customfield_is_public_alter_customfield_attribute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='attribute',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='custom_field', to='eav.attribute'),
        ),
    ]
