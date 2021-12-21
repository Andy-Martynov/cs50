from django.contrib import admin

from .models import Post, Follow, Like

admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Like)
