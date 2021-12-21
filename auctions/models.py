# from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

listing_images = 'auctions/images/listing/'

from account.models import User
# class User(AbstractUser):
    # pass


class Category(models.Model):
    title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.title}"


class Listing(models.Model):
    title = models.CharField(max_length=88)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    start_price = models.IntegerField()
    current_price = models.IntegerField(default=0)
    image = models.ImageField(upload_to=listing_images, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"""{self.title}\n
            desription: {self.description}\n
            category: {self.category}\n
            start: {self.start_price}\n
            current: {self.current_price}\n
            active: {self.active}
            image: {self.image}
"""
    def get_absolute_url(self):
        return reverse('auctions:listing-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}: {self.text} ({self.created}) on {self.listing.title} by {self.author}"

    def get_absolute_url(self):
        return reverse('auctions:comment-detail', kwargs={'pk': self.pk})


class Watch(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"on {self.listing.title} by {self.user} [{ self.id }]"


class Bid(models.Model):
    price = models.IntegerField()
    created = models.DateTimeField(auto_now=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.price} on {self.listing.title} by {self.author} ({self.created})"



