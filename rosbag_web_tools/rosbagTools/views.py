#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.conf import settings

from .models import RosbagInfo

import rosbag

sys.path.append('/opt/ros/melodic/lib/python2.7/dist-packages')

UPLOADE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'uploads')


# https://qiita.com/nnsnodnb/items/f7b1b0b7f2099e403947
def upload_form(request):
  if request.method != 'POST':
    return render(request, 'rosbagTools/form.html')

  uploaded_file = request.FILES['file']
  dst_path = os.path.join(UPLOADE_DIR, '{0:%Y%m%d}'.format(datetime.datetime.now()))
  # '{0:%Y%m%d_%H%M%S}'.format(datetime.datetime.now()))
  if not os.path.exists(dst_path):
    os.makedirs(dst_path)
  dst_path = os.path.join(dst_path, uploaded_file.name)

  with open(dst_path, 'wb') as f:
    for chunk in uploaded_file.chunks():
      f.write(chunk)

  baginfo = RosbagInfo()
  bag = rosbag.Bag(dst_path)

  baginfo.bag_name = bag._filename
  baginfo.bag_size = bag.size
  baginfo.content_topics = sorted(set([c.topic for c in bag._get_connections()]))
  baginfo.content_types = [list(bag._get_connections(topic))[0].datatype for topic in baginfo.content_topics]

  baginfo.save()

  return redirect('rosbagTools:complete')


def complete(request):
  return render(request, 'rosbagTools/complete.html')
