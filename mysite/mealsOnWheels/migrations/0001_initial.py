# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mealsOnWheels.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodTruck',
            fields=[
                ('key', models.CharField(max_length=50, unique=True, serialize=False, verbose_name=b'Key', primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Truck Name')),
                ('foodType', models.CharField(max_length=200, verbose_name=b'Truck Food Type')),
                ('location', models.CharField(max_length=200, null=True, verbose_name=b'Truck Location')),
            ],
        ),
        migrations.CreateModel(
            name='LastImportDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(null=True)),
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
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', mealsOnWheels.models.Integer010Field(help_text=b'rate must be between 0 - 10', blank=True)),
                ('pub_date', models.DateField()),
                ('foodtruck', models.ForeignKey(to='mealsOnWheels.FoodTruck')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserJSONObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json_object', models.TextField()),
                ('location', models.OneToOneField(null=True, to='mealsOnWheels.Position')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activation_key', models.CharField(max_length=40, blank=True)),
                ('key_expires', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User profiles',
            },
        ),
        migrations.AddField(
            model_name='foodtruck',
            name='position',
            field=models.ForeignKey(to='mealsOnWheels.Position'),
        ),
    ]
