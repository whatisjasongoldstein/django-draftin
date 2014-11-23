# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('draftin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='auto_publish',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='draft',
            name='published',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
