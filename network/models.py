from django.db import models
from django.urls import reverse

from account.models import User

class Post(models.Model) :
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comment = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.id} {self.author.username} created {self.created}"

    def get_absolute_url(self):
        return reverse('network:index')


class Follow(models.Model) :
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_i')
    whom = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_me')

    def __str__(self):
        return f"{self.who.username} follows {self.whom.username}"


class Like(models.Model) :
    who = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_i')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_me')

    def __str__(self):
        return f"{self.who.username} likes {self.post.id} by {self.post.author.username}"
