# Generated by Django 5.1 on 2024-09-04 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_rename_app_tracked_time_apps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracked_time',
            name='day',
            field=models.IntegerField(default=4),
        ),
    ]
