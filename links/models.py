from django.db import models

from account.models import User
from folders.models import Folder

class Link(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="links")
    url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    # title = models.CharField(max_length=200, blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)
    # description = models.TextField(blank=True, null=True)
    # image = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name}"

