# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0007_auto_20150608_0347'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodTruck',
            fields=[
                ('key', models.CharField(max_length=50, serialize=False, verbose_name=b'Key', primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Truck Name')),
                ('foodType', models.CharField(max_length=200, verbose_name=b'Truck Food Type')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
        ),
    ]
