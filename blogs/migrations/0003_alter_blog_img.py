# Generated by Django 5.1.2 on 2025-02-13 13:08

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_blog_estore_tag_estore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='img',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
