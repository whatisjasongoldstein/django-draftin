# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-02 19:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draftin', '0005_auto_20151213_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='name',
            field=models.CharField(default=b'', max_length=255),
        ),
    ]
