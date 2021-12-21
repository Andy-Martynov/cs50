from django.contrib.auth.models import AbstractUser
from django.db import models
import os

user_images = 'account/images/'

class User(AbstractUser):
    image =     models.ImageField(upload_to=user_images, blank=True, null=True, default='account/images/x.png')
    latitude =  models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=13, default=0)
    longitude = models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=13, default=0)
    tag =       models.CharField(max_length=5, blank=True, null=True)
    marker =    models.CharField(max_length=400, blank=True, null=True)
    token =     models.IntegerField(default=0)
    is_guest =  models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username.replace('_', ' ')}"

    def filename(self):
        return os.path.basename(self.image.url)

    def fullname(self):
        return 'media/account/images/' + os.path.basename(self.image.url)

    def imagefile(self):
        return '/account/images/' + os.path.basename(self.image.url)

    def serialize(self):
        image = None
        if self.image:
            image = self.image.url
        return {
            "id": self.id,
            "username": self.username.replace('_', ' '),
            # "latitude": str(self.latitude),
            # "longitude": str(self.longitude),
            # "tag": self.tag,
            # "marker": self.marker,
            'image': image,
        }


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(User, through='Membership', through_fields=('group', 'user'), related_name='member_in')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='groups_created')

    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        members = []
        memberships = Membership.objects.filter(group=self)
        for membership in memberships:
            members.append(membership.user.serialize())

        return {
            "id": self.id,
            'name': self.name,
            "members": members,
            'creator': self.creator.serialize(),
        }


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')

    def __str__(self):
        return f"{self.user.username} => {self.group.name}"

