# Generated by Django 4.0.3 on 2022-05-23 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_specialization_profile_order_perf_spec'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='was_edited',
            field=models.BooleanField(default=False),
        ),
    ]
