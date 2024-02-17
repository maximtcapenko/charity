# Generated by Django 4.2.10 on 2024-02-17 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0008_remove_mailingtemplate_notes'),
        ('submissions', '0004_alter_submission_mailing_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='mailing_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='submissions', to='mailings.mailingtemplate'),
        ),
    ]