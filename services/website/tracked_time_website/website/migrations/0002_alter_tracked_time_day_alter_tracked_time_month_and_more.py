# Generated by Django 5.1 on 2024-09-02 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracked_time',
            name='day',
            field=models.IntegerField(default=3, editable=False),
        ),
        migrations.AlterField(
            model_name='tracked_time',
            name='month',
            field=models.IntegerField(default=9, editable=False),
        ),
        migrations.AlterField(
            model_name='tracked_time',
            name='year',
            field=models.IntegerField(default=2024, editable=False),
        ),
    ]
