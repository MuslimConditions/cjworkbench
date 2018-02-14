# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-09 01:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0090_merge_20180201_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='example',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='selected_wf_module',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]