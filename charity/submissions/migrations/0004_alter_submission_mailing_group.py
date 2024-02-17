# Generated by Django 4.2.10 on 2024-02-17 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0008_remove_mailingtemplate_notes'),
        ('submissions', '0003_alter_submission_is_draft_alter_submission_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='mailing_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submissions', to='mailings.mailinggroup'),
        ),
    ]
