# Generated by Django 2.0.3 on 2018-05-26 12:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_auto_20180526_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 26, 12, 54, 8, 332131)),
        ),
    ]