# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-27 06:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hf', '0003_userinterestnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='hifipost',
            name='attachment_thumb',
            field=models.FileField(null=True, upload_to='attachments/thumb'),
        ),
    ]
