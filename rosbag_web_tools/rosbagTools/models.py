from django.db import models
from django_mysql import models as sql_models
from django.core.validators import FileExtensionValidator


# https://qiita.com/okoppe8/items/86776b8df566a4513e96
# class UploadRosbagFile(models.Model):
#   file = models.FileField(upload_to='uploads/%YYYY%mm%dd/',
#                           verbose_name='bag file',# class UploadRosbagFile(models.Model):
#   file = models.FileField(upload_to='uploads/%YYYY%mm%dd/',
#                           verbose_name='bag file',
#                           validators=[FileExtensionValidator(['bag', ])])

#                           validators=[FileExtensionValidator(['bag', ])])


class RosbagInfo(models.Model):
  bag_name = models.TextField()
  bag_path = models.TextField()
  bag_size = models.FloatField()
  content_topics = sql_models.ListTextField(models.CharField(max_length=30))
  content_types = sql_models.ListTextField(models.CharField(max_length=30))
  content_msgnum = sql_models.ListTextField(models.CharField(max_length=30))


class RosbagParsedData(models.Model):
  file = models.FileField()
