# Generated by Django 5.0 on 2024-01-11 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0003_alter_approvement_options_alter_contribution_options_and_more'),
        ('tasks', '0002_alter_comment_options_alter_expense_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='approvements',
            field=models.ManyToManyField(related_name='approved_expenses', to='funds.approvement'),
        ),
    ]
