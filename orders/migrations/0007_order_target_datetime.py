# Generated by Django 4.0.3 on 2022-06-24 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_flat_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='target_datetime',
            field=models.DateTimeField(null=True),
        ),
    ]
