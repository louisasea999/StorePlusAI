# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-06-07 11:30
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('find', '0014_auto_20180529_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='allfaces',
            name='blur',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='eyegaze',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='facequality',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='headpose',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='mostlike_score',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='mouthstatus',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='allfaces',
            name='smile',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
