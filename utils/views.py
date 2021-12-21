from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import os

from mysite import settings
from account.models import User
from album.models import Album, Item

def file_tree(startpath) :                # -------------- FILE_TREE -----------
    tree = dict()
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        dir_name = os.path.basename(root)
        if level == 1 :
            images = []
            for f in files:
                file = os.path.join(root,f)
                images.append(file)
            tree[int(dir_name)] = images
    keys = []
    for key in tree :
        keys.append(key)
    print(keys)
    keys.sort()
    print(keys)
    sorted_tree = dict()
    for key in keys :
        sorted_tree[key] = tree[key]
    return sorted_tree

@login_required
def album_files(request, mode=None) :
    album_thumbs = set()
    album_images = set()
    album_musics = set()
    album_watermarks = set()
    item_thumbs = set()
    item_objects = set()
    nothing = set()

    albums = Album.objects.all()
    for album in albums :
        if album.thumb :
            album_thumbs.add(album.thumbname())
        if album.image :
            album_images.add(album.imagename())
        if album.music :
            album_musics.add(album.musicname())
        if album.watermark :
            album_watermarks.add(album.watermarkname())

    items = Item.objects.all()
    for item in items :
        if item.thumb :
            thumb = item.thumb
            thumb = thumb.split(os.path.sep)[-1]
            item_thumbs.add(thumb)
        if item.file :
            item_objects.add(item.filename())

    dir = os.path.join(settings.MEDIA_ROOT, 'album', 'images')
    album_files = os.listdir(dir)
    for file in album_files :
        if not ((file in album_thumbs) or (file in album_images) or (file in album_musics)) :
            nothing.add(os.path.join(settings.MEDIA_ROOT, 'album', 'images', file))

    dir = os.path.join(settings.MEDIA_ROOT, 'album', 'watermarks')
    watermark_files = os.listdir(dir)
    for file in watermark_files :
        messages.info(request, f"check {file}", extra_tags='alert-info')
        if not (file in album_watermarks) :
            messages.info(request, f"unused {file}", extra_tags='alert-warning')
            nothing.add(os.path.join(settings.MEDIA_ROOT, 'album', 'watermarks', file))
        else :
            messages.info(request, f"in use {file}", extra_tags='alert-success')

    dir = os.path.join(settings.MEDIA_ROOT, 'album', 'items', 'images')
    item_files = os.listdir(dir)
    for file in item_files :
        if not ((file in item_thumbs) or (file in item_objects)) :
            nothing.add(os.path.join(settings.MEDIA_ROOT, 'album', 'items', 'images', file))

    if mode == 'delete' :
        for file in nothing :
            os.remove(file)

    return render(request, "utils/album_files.html", {
        "dir":dir,
        "album_musics":album_musics,
        "album_thumbs":album_thumbs,
        "album_images":album_images,
        "album_watermarks":album_watermarks,
        "item_thumbs":item_thumbs,
        "item_objects":item_objects,
        "album_files":album_files,
        "watermark_files":watermark_files,
        "item_files":item_files,
        "nothing":nothing,
        })

@login_required
def account_files(request, mode=None) :
    account_images = set()
    nothing = set()

    users = User.objects.all()
    for user in users :
        if user.image :
            account_images.add(user.filename())

    dir = os.path.join(settings.MEDIA_ROOT, 'account', 'images')
    account_files = os.listdir(dir)
    for file in account_files :
        if not (file in account_images) :
            nothing.add(os.path.join(settings.MEDIA_ROOT, 'account', 'images', file))

    if mode == 'delete' :
        for file in nothing :
            os.remove(file)

    return render(request, "utils/account_files.html", {
        "dir":dir,
        "account_images":account_images,
        "account_files":account_files,
        "nothing":nothing,
        })

