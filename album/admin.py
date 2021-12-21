from django.contrib import admin

from .models import Album, Item, Extention, Animation

admin.site.register(Album)
admin.site.register(Item)
admin.site.register(Extention)
admin.site.register(Animation)