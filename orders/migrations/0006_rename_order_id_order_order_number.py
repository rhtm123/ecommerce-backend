# Generated by Django 5.1.2 on 2025-02-10 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_remove_order_status_remove_order_total_items_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_id',
            new_name='order_number',
        ),
    ]
