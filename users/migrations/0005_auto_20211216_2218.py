# Generated by Django 2.2.5 on 2021-12-16 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_email_secret'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='email_confirmed',
            new_name='email_verify',
        ),
    ]
