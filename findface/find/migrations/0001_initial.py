# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-20 15:48
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllFaces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageid', models.CharField(max_length=24)),
                ('facetoken', models.CharField(max_length=32, null=True)),
                ('picpath', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=6, null=True)),
                ('age', models.IntegerField(null=True)),
                ('eyestatus', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('emotion', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('ethnicity', models.CharField(max_length=5, null=True)),
                ('male_score', models.FloatField(null=True)),
                ('female_score', models.FloatField(null=True)),
                ('skinstatus', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('chstamp', models.DateTimeField(auto_now=True)),
                ('freeinfo', models.CharField(max_length=60, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ErrFaces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picpath', models.CharField(max_length=100)),
                ('errmsg', models.CharField(max_length=60, null=True)),
                ('chstamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='allfaces',
            unique_together=set([('imageid', 'facetoken')]),
        ),
    ]
