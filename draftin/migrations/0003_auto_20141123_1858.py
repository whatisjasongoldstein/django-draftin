# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('draftin', '0002_auto_20141123_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='uuid',
            field=models.CharField(max_length=255, editable=False),
        ),
        migrations.AlterField(
            model_name='draft',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]
