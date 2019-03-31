#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'rosbagTools'
urlpatterns = [
  path('', views.upload_form, name='form'),
  path('complete/', views.complete, name='complete'),
]
