# Generated by Django 5.1.2 on 2025-07-11 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
