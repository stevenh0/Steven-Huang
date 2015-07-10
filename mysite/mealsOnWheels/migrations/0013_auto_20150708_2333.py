# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0012_review_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodtruck',
            name='key',
            field=models.CharField(max_length=50, unique=True, serialize=False, verbose_name=b'Key', primary_key=True),
        ),
    ]
