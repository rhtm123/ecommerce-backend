# Generated by Django 5.1.2 on 2025-01-16 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_rename_listing_feature_product_listing'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productlistingimage',
            old_name='listing',
            new_name='product_listing',
        ),
    ]
