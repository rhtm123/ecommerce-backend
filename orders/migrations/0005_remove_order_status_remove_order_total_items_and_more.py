# Generated by Django 5.1.2 on 2025-02-10 07:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_total_items'),
        ('products', '0010_alter_productlisting_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_items',
        ),
        migrations.RemoveField(
            model_name='order',
            name='tracking_number',
        ),
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(blank=True, max_length=24, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='product_listing_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='total_units',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, help_text='Total price of all items including taxes and discounts', max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.order'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Price per unit at time of purchase', max_digits=10),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product_listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_listing_order_items', to='products.productlisting'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(help_text='Number of units ordered for this product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('processing', 'processing'), ('shipped', 'shipped'), ('delivered', 'delivered'), ('canceled', 'canceled')], default='pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, help_text='Total price for this product line (quantity × unit_price)', max_digits=10),
        ),
        migrations.CreateModel(
            name='DeliveryPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('processing', 'processing'), ('shipped', 'shipped'), ('delivered', 'delivered'), ('canceled', 'canceled')], default='processing', max_length=50)),
                ('product_listing_count', models.PositiveIntegerField(default=0, help_text='Number of distinct products in this package')),
                ('total_units', models.PositiveIntegerField(default=0, help_text='Total number of items in this package')),
                ('shipped_date', models.DateTimeField(blank=True, null=True)),
                ('delivered_date', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='PackageItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Number of units included in this package')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_item_package_item', to='orders.orderitem')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='package_items', to='orders.deliverypackage')),
            ],
        ),
    ]
