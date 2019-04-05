#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import cv2

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.template.context_processors import csrf
from django.conf import settings

from .models import RosbagInfo

import rosbag
from cv_bridge import CvBridge, CvBridgeError

sys.path.append('/opt/ros/melodic/lib/python2.7/dist-packages')

UPLOADE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'uploaded')
DOWNLOADING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'downloading')


# https://qiita.com/nnsnodnb/items/f7b1b0b7f2099e403947
def upload_form(request):
  if request.method == 'GET':
    return render(request, 'rosbagTools/form.html')
  if request.method != 'POST':
    return

  uploaded_file = request.FILES['file']
  dstpath = os.path.join(UPLOADE_DIR, '{0:%Y%m%d}'.format(datetime.datetime.now()))
  if not os.path.exists(dstpath):
    os.makedirs(dstpath)
  dstpath = os.path.join(dstpath, uploaded_file.name)

  if not os.path.exists(dstpath):
    with open(dstpath, 'wb') as f:
      for chunk in uploaded_file.chunks():
        f.write(chunk)

  baginfo = RosbagInfo()
  bag = rosbag.Bag(dstpath)

  baginfo.bag_path = bag._filename
  baginfo.bag_name = os.path.basename(baginfo.bag_path)
  baginfo.bag_size = bag.size
  baginfo.content_topics = sorted(set([c.topic for c in bag._get_connections()]))
  baginfo.content_types = [list(bag._get_connections(topic))[0].datatype for topic in baginfo.content_topics]
  baginfo.content_msgnum = [len(bag.read_messages(topic)) for topic in baginfo.content_topics]

  baginfo.save()
  return redirect('rosbagTools:complete', pk=baginfo.pk)


def complete(request, pk):
  baginfo = get_object_or_404(RosbagInfo, pk=pk)

  return render(request, 'rosbagTools/complete.html', {
    'pk': pk,
    'bagname': baginfo.bag_name,
    'encoding_formats': ['mono8', 'mono16', 'bgr8', 'rgb8', 'bgra8', 'rgba8'],
    'extension_formats': ['png', 'pgm', 'jpg'],
    'topics_and_types': [{'topicidx': idx,
                          'topic': to,
                          'type': ty} for idx, (to, ty) in enumerate(zip(baginfo.content_topics,
                                                                         baginfo.content_types))]
  })


# https://narito.ninja/blog/detail/93/
def download_zip(request, pk):
  dl_topicidx_list = request.POST.getlist('zip')
  dl_image_extention = {ext.split('_')[0]: ext.split('_')[1] for ext in request.POST.getlist('extention')}
  if len(dl_topicidx_list) == 0:
    return redirect('rosbagTools:complete', pk=pk)
  baginfo = get_object_or_404(RosbagInfo, pk=pk)
  bagdata = rosbag.Bag(baginfo.bag_path)
  dstpath = os.path.join(DOWNLOADING_DIR, '{0:%Y%m%d}/{0:%H%M%S%f}'.format(datetime.datetime.now()))
  if not os.path.exists(dstpath):
    os.makedirs(dstpath)

  for topicidx in [int(tidx) for tidx in dl_topicidx_list]:
    topicname, topictype = baginfo.content_topics[topicidx], baginfo.content_types[topicidx]
    if topictype == 'sensor_msgs/Image':
      img_dstpath = os.path.join(dstpath, topicname[1:].replace('/', '-'))
      ext = dl_image_extention[topicidx]
      zerofillnum = len(str(baginfo.content_msgnum[topicidx])) + 1
      for idx, (_, msg, ts) in enumerate(bagdata.read_messages(topicname)):
        try:
          cvimg = CvBridge().imgmsg_to_cv2(msg)
          cv2.imwrite(os.path.join(img_dstpath, '{0}.{1}'.format(str(idx).zfill(zerofillnum), ext)),
                      cvimg)
        except CvBridgeError as cverror:
          print(cverror)
      else:
        pass

  return redirect('rosbagTools:complete', pk=pk)


def download(request, pk, topicidx):
  print(topicidx)
  baginfo = get_object_or_404(RosbagInfo, pk=pk)
  return redirect('rosbagTools:complete', pk=baginfo.pk)
