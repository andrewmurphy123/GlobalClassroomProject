# Generated by Django 4.0.3 on 2022-04-23 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_alter_stock_unique_together_stock_product_size_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Stock',
        ),
    ]
