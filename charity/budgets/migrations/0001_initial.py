# Generated by Django 5.0 on 2023-12-21 17:46

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('funds', '0005_delete_ward'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('start_period_date', models.DateField()),
                ('end_period_date', models.DateField()),
                ('is_closed', models.BooleanField(default=False)),
                ('approvement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='funds.approvement')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('fund', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='budgets', to='funds.fund')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('approvement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='funds.approvement')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='incomes', to='budgets.budget')),
                ('contribution', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='funds.contribution')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
