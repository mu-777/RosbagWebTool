#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.template.context_processors import csrf
from django.conf import settings

from .models import RosbagInfo

import rosbag

sys.path.append('/opt/ros/melodic/lib/python2.7/dist-packages')

UPLOADE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'uploads')


# https://qiita.com/nnsnodnb/items/f7b1b0b7f2099e403947
def upload_form(request):
  if request.method == 'GET':
    return render(request, 'rosbagTools/form.html')
  if request.method != 'POST':
    return

  uploaded_file = request.FILES['file']
  dst_path = os.path.join(UPLOADE_DIR, '{0:%Y%m%d}'.format(datetime.datetime.now()))
  if not os.path.exists(dst_path):
    os.makedirs(dst_path)
  dst_path = os.path.join(dst_path, uploaded_file.name)

  if not os.path.exists(dst_path):
    with open(dst_path, 'wb') as f:
      for chunk in uploaded_file.chunks():
        f.write(chunk)

  baginfo = RosbagInfo()
  bag = rosbag.Bag(dst_path)

  baginfo.bag_path = bag._filename
  baginfo.bag_name = os.path.basename(baginfo.bag_path)
  baginfo.bag_size = bag.size
  baginfo.content_topics = sorted(set([c.topic for c in bag._get_connections()]))
  baginfo.content_types = [list(bag._get_connections(topic))[0].datatype for topic in baginfo.content_topics]

  baginfo.save()
  return redirect('rosbagTools:complete', pk=baginfo.pk)


def complete(request, pk):
  baginfo = get_object_or_404(RosbagInfo, pk=pk)

  return render(request, 'rosbagTools/complete.html', {
    'pk': pk,
    'bagname': baginfo.bag_name,
    'topics_and_types': [{'topicidx': idx,
                          'topic': to,
                          'type': ty} for idx, (to, ty) in enumerate(zip(baginfo.content_topics,
                                                                         baginfo.content_types))]
  })


def download(request, pk, topicidx):
  print(topicidx)
  baginfo = get_object_or_404(RosbagInfo, pk=pk)
  return HttpResponse('download: {0}'.format(baginfo.content_topics[topicidx]))
