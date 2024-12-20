# Generated by Django 5.1.2 on 2024-12-20 06:21

import imagekit.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productlistingimage',
            name='is_main',
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='feature',
            name='slug',
            field=models.SlugField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='productlisting',
            name='main_image',
            field=imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='kb/product_listings/'),
        ),
        migrations.AddField(
            model_name='productlisting',
            name='slug',
            field=models.SlugField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='feature',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='feature',
            name='value',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='productlistingimage',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(upload_to='kb/product_listings/'),
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
