# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-05-29 19:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('find', '0013_auto_20180528_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='errfaces',
            name='fixmsg',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='errfaces',
            name='errmsg',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
