# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0008_foodtruck_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodtruck',
            name='position',
            field=models.ForeignKey(default=0, to='mealsOnWheels.Position'),
            preserve_default=False,
        ),
    ]
