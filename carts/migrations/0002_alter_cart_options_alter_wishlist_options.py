# Generated by Django 5.1.2 on 2025-02-21 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='wishlist',
            options={'ordering': ['-id']},
        ),
    ]
