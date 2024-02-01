# Generated by Django 4.2.9 on 2024-01-27 23:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('funds', '0006_contributor_cover'),
        ('eav', '0011_alter_attribute_id_alter_enumgroup_id_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='eav.attribute')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('fund', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='funds.fund')),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
            },
        ),
    ]