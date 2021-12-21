from django.db import models

import os

from account.models import User

location_images = 'meeting/images/'

class Location(models.Model) :
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="locations")
    latitude = models.DecimalField(null=True, blank=True, max_digits=19, decimal_places=16, default=0)
    longitude = models.DecimalField(null=True, blank=True, max_digits=19, decimal_places=16, default=0)
    name = models.CharField(max_length=200, blank=True, null=True)
    tag = models.CharField(max_length=5, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    marker = models.CharField(max_length=400, blank=True, null=True)
    image = models.ImageField(upload_to=location_images, blank=True, null=True, default='meeting/images/big_pin.png')

    def __str__(self):
        return f"{self.name}"

    def filename(self):
        return os.path.basename(self.image.url)

    def fullname(self):
        return 'media/' + location_images + os.path.basename(self.image.url)

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name": self.name,
            "address": self.address,
            "tag": self.tag,
            "marker": self.marker,
            "image": self.image.url
        }


class Meeting(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meetings")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="meetings", blank=True, null=True)
    name = models.CharField(max_length=250)
    memo = models.TextField(null=True, blank=True)
    start = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    members = models.ManyToManyField(
        User,
        through='Participation',
        through_fields=('meeting', 'user'),
    )

    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner.username,
            "name": self.name,
            "memo": self.memo
        }


class Participation(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



