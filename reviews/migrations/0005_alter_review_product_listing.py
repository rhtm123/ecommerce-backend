# Generated by Django 5.1.2 on 2025-02-07 07:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_productlisting_review_count'),
        ('reviews', '0004_review_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='product_listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_listing_reviews', to='products.productlisting'),
        ),
    ]
