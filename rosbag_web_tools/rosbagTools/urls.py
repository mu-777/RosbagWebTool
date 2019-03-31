#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'rosbagTools'
urlpatterns = [
  path('', views.upload_form, name='form'),
  path('<int:pk>/complete/', views.complete, name='complete'),
  path('<int:pk>/<int:topicidx>/download/', views.download, name='download'),
]
