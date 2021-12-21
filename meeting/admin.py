from django.contrib import admin

from .models import Location, Meeting, Participation

admin.site.register(Location)
admin.site.register(Meeting)
admin.site.register(Participation)
