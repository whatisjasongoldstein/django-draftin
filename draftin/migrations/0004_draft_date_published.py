# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('draftin', '0003_auto_20141123_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='draft',
            name='date_published',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
