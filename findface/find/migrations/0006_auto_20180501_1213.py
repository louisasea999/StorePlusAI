# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-05-01 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('find', '0005_auto_20180501_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='allfaces',
            name='snapint',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='snapseq',
            field=models.IntegerField(null=True),
        ),
    ]
