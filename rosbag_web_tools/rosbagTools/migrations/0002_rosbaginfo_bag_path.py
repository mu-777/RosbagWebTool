# Generated by Django 2.1.7 on 2019-03-31 11:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rosbagTools', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rosbaginfo',
            name='bag_path',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]