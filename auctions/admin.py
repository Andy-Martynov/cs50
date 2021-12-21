from django.contrib import admin

from .models import Category, Listing, Comment, Watch, Bid

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Watch)
admin.site.register(Bid)