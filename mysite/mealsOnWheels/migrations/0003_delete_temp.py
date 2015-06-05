# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0002_temp'),
    ]

    operations = [
        migrations.DeleteModel(
            name='temp',
        ),
    ]
