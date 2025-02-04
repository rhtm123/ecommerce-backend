# Generated by Django 5.1.2 on 2025-02-03 16:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_orderitem_created_orderitem_status_orderitem_updated'),
        ('reviews', '0002_review_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='order_item',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_item_reviews', to='orders.orderitem'),
        ),
    ]
