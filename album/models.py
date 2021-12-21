from django.db import models
from django.urls import reverse

import os

from account.models import User

albums_images = 'album/images/'
albums_watermarks = 'album/watermarks/'
items_images = 'album/items/images/'

class Animation(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="animations")
    title = models.CharField(max_length=30, blank=True, null=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    prefix = models.CharField(max_length=200, blank=True, null=True)
    duration = models.IntegerField(default=10)
    delay = models.FloatField(default=0)
    count = models.CharField(max_length=20, default='infinite')
    direction = models.CharField(max_length=20, default='normal')
    timing = models.CharField(max_length=20, default='ease')
    fill = models.CharField(max_length=20, default='none')
    keyframes = models.CharField(max_length=1000, blank=True, null=True)
    session_key = models.CharField(max_length=50, default='none', blank=True, null=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse('album:animation_detail', kwargs={'pk': self.pk})

class Album(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="childs")
    title = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    tag = models.CharField(max_length=200, blank=True, null=True)
    thumb = models.ImageField(upload_to=albums_images, blank=True, null=True, default='album/images/folder_240.png')
    image = models.ImageField(upload_to=albums_images, blank=True, null=True, )
    watermark = models.ImageField(upload_to=albums_watermarks, blank=True, null=True, )
    interval = models.IntegerField(default=300)
    opacity = models.FloatField(default=0.5)
    music = models.FileField(upload_to=albums_images, blank=True, null=True, )
    def_thumb_width = models.IntegerField(default=240)
    def_thumb_height = models.IntegerField(default=180)
    max_image_width = models.IntegerField(default=1366, blank=True, null=True, )
    max_image_height = models.IntegerField(default=786, blank=True, null=True, )
    level = models.IntegerField(default=0)
    animation = models.ForeignKey(Animation, on_delete=models.SET_NULL, blank=True, null=True, related_name="albums")

    def __str__(self):
        return f"{self.title} by {self.user}"

    def imagename(self):
        return os.path.basename(self.image.url)

    def imagefullname(self):
        return 'media/' + albums_images + os.path.basename(self.image.url)

    def thumbname(self):
        return os.path.basename(self.thumb.url)

    def thumbfullname(self):
        return 'media/' + albums_images + os.path.basename(self.thumb.url)

    def watermarkname(self):
        return os.path.basename(self.watermark.url)

    def watermarkfullname(self):
        return 'media/' + albums_watermarks + os.path.basename(self.watermark.url)

    def musicname(self):
        return os.path.basename(self.music.url)

    def musicfullname(self):
        return 'media/' + albums_images + os.path.basename(self.music.url)

    def get_absolute_url(self):
        return reverse('album:album_setup', kwargs={'id': self.pk})


IMAGE = 'IMG'
VIDEO = 'VID'
DOCUMENT = 'DOC'
UNKNOWN = 'UKN'
LINK = 'LNK'
YOUTUBE = 'YTB'
MODE_CHOICES = [
    (IMAGE, 'Image'),
    (VIDEO, 'Video'),
    (DOCUMENT, 'Document'),
    (UNKNOWN, 'Unknown'),
    (LINK, 'Link'),
    (YOUTUBE, 'YouTube'),
]


class Item(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="items")
    animation = models.ForeignKey(Animation, on_delete=models.SET_NULL, blank=True, null=True, related_name="items")
    title = models.CharField(max_length=200, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    mode = models.CharField(max_length=3, choices=MODE_CHOICES, default=IMAGE,)
    tag = models.CharField(max_length=200, blank=True, null=True)
    thumb = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to=items_images, blank=True, null=True, )
    youtube =  models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"[{self.id}] {self.title}"

    def filename(self):
        return os.path.basename(self.file.url)

    def filefullname(self):
        return 'media/' + albums_images + os.path.basename(self.file.url)

    def get_absolute_url(self):
        if self.mode == 'LNK':
            return reverse('album:user_links')
        return reverse('album:item_setup', kwargs={'id': self.pk})

class Extention(models.Model):
    ext = models.CharField(max_length=10)
    mode = models.CharField(max_length=3, choices=MODE_CHOICES, default=IMAGE,)

    def __str__(self):
        return f"{self.ext} => {self.mode}"

