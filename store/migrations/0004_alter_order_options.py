# Generated by Django 4.1.4 on 2022-12-26 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_customer_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': [('cancel_order', 'Can cancel order')]},
        ),
    ]
