# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-14 19:45
from __future__ import unicode_literals

from django.db import migrations

def update_media_files(apps, schema_editor):
    StoredObject = apps.get_model('server', 'StoredObject')
    for object in StoredObject.objects.filter(file__startswith='media/'):
        filename = str(object.file)
        filename = filename[6:]
        object.file = filename
        object.save(update_fields=['file'])

class Migration(migrations.Migration):

    dependencies = [
        ('server', '0065_auto_20170914_1657'),
    ]

    operations = [
        migrations.RunPython(update_media_files),
    ]
