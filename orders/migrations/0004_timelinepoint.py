# Generated by Django 4.0.3 on 2022-05-28 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_comment_is_active_comment_was_edited'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimelinePoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline', to='orders.order')),
            ],
        ),
    ]