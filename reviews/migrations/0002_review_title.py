# Generated by Django 5.1.2 on 2025-02-03 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
