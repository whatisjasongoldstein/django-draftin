# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-10 00:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draftin', '0007_draft_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draft',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
