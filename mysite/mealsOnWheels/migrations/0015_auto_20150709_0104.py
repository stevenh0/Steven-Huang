# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0014_userjsonobject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userjsonobject',
            name='location',
            field=models.OneToOneField(null=True, to='mealsOnWheels.Position'),
        ),
    ]
