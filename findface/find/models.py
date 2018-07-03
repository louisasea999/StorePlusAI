# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
#from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import JSONField


class AllFaces(models.Model):
    imageid = models.CharField(max_length=24,null=True)
    facetoken = models.CharField(max_length=32,unique=True,db_index=True)
    videopath = models.CharField(max_length=200)
    picname = models.CharField(max_length=40,null=True)
    pictime = models.DateTimeField(null=True)
    #pictime = models.CharField(max_length=20,null=True)
    snapint = models.IntegerField(null=True)
    snapseq = models.IntegerField(null=True)
    #face attributes
    gender = models.CharField(max_length=6,null=True)
    age = models.IntegerField(null=True)
    smile = JSONField(null=True)
    headpose = JSONField(null=True)
    blur = JSONField(null=True)
    eyestatus = JSONField(null=True)
    emotion = JSONField(null=True)
    facequality = JSONField(null=True)
    ethnicity = models.CharField(max_length=5,null=True)
    male_score = models.FloatField(null=True)
    female_score = models.FloatField(null=True)
    mouthstatus = JSONField(null=True)
    eyegaze = JSONField(null=True)
    skinstatus = JSONField(null=True)
    #face attributes
    freeinfo = models.CharField(max_length=60,null=True)
    faceset_status = models.CharField(max_length=1,default='N')
    faceset_outerid = models.CharField(max_length=255,null=True)
    mostlike_score = models.FloatField(null=True)
    
class ErrFaces(models.Model):
    picpath = models.CharField(max_length=100)
    errmsg = models.CharField(max_length=200,null=True)
    fixmsg = models.CharField(max_length=200,null=True)
    chstamp = models.DateTimeField(auto_now=True)
    fixstatus = models.CharField(max_length=1,null=True)
    snapint = models.IntegerField(null=True)
    snapseq = models.IntegerField(null=True)

class AllFaceSets(models.Model):
    faceset_token = models.CharField(max_length=32,unique=True)
    face_tokens = JSONField()
    face_count = models.IntegerField(null=True)
    outer_id = models.CharField(max_length=255,unique=True)

    