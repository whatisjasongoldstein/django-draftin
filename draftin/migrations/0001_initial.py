# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('uuid', models.CharField(max_length=255)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Draft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('draft_id', models.IntegerField()),
                ('name', models.CharField(max_length=512)),
                ('content', models.TextField()),
                ('content_html', models.TextField()),
                ('draftin_user_id', models.IntegerField(null=True, blank=True)),
                ('draftin_user_email', models.EmailField(max_length=75)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('last_synced_at', models.DateTimeField(auto_now=True)),
                ('collection', models.ForeignKey(to='draftin.Collection')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
