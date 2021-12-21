from django.urls import path

from . import views

app_name = 'project0'
urlpatterns = [
    path("", views.index, name="index"),
    path("languages", views.languages, name="languages"),
    path("poetry", views.poetry, name="poetry"),
    path("photos", views.photos, name="photos"),
]
