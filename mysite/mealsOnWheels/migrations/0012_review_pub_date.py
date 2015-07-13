# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mealsOnWheels', '0011_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='pub_date',
            field=models.DateField(default=datetime.datetime(2015, 7, 8, 19, 17, 44, 554892, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
