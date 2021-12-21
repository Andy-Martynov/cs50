from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

import os
import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from common.instruments import empty_folder, file_tree

from mysite import settings

from album.models import Animation

@login_required
def index(request) :
    return render(request, "adminboard/index.html")

def image_url(name, folder='graphs'):
    return os.path.join(settings.MEDIA_URL, folder, name)

@login_required
def files(request, folder='') :
    if folder == '':
        folder = settings.BASE_DIR
    else:
        folder = folder.replace('?', '/')
    context = {}
    tree = file_tree(folder)
    for item in tree:
        item['left'] = item['level'] * 30
    context['tree'] = tree

    empty_folder(os.path.join(settings.MEDIA_ROOT, 'graphs'))

    file_sizes = pd.DataFrame(tree[0]['file_sizes'])
    dir_sizes = pd.DataFrame(tree[0]['dir_sizes'])

    shape = file_sizes.shape
    if shape[0] > 0:
        fig = plt.figure(figsize=[20, 20])
        ax = fig.add_subplot(111)
        ax.pie(file_sizes['size'], labels=file_sizes['name'], textprops={'fontsize': 20})
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.legend(fontsize=20)
        ax.set_title("FIlES",fontsize=20)
        name = 'files.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        plt.clf()
        context['files'] = image_url(name)

    shape = dir_sizes.shape
    if shape[0] > 0:
        fig = plt.figure(figsize=[20, 20])
        ax = fig.add_subplot(111)
        ax.pie(dir_sizes['size'], labels=dir_sizes['name'], textprops={'fontsize': 20})
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.legend(fontsize=20)
        ax.set_title("DIRS", fontsize=20)
        name = 'dirs.png'
        fn = os.path.join(settings.MEDIA_ROOT, 'graphs', name)
        fig.savefig(fn, bbox_inches='tight')
        plt.clf()
        context['dirs'] = image_url(name)
    return render(request, "adminboard/files.html", context)

@login_required
def db_clean(request):

    count1 = Session.objects.count()
    messages.info(request, f"Sessions db count = {count1}", extra_tags='alert-info')

    Session.objects.all().delete()
    count2 = Session.objects.count()
    messages.info(request, f"Sessions db count = {count2}", extra_tags='alert-success')

    context = {}
    context['count1'] = count1
    context['count2'] = count2

    context['db'] = settings.DATABASES['default']['NAME']

    anim_count = Animation.objects.count()
    context['anim_count'] = anim_count

    Animation.objects.exclude(session_key__exact=None).delete()

    anim_count = Animation.objects.count()
    context['anim_count2'] = anim_count

    return render(request, "adminboard/db_clean.html", context)

