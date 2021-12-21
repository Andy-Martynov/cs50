from django.urls import path

from . import views

app_name = 'watermark'
urlpatterns = [
    path("", views.reset, name="start"),
    path("index", views.index, name="index"),

    path("load", views.load, name="load"),
    path("view/<str:name>/<str:opacity>/<int:interval>", views.view, name="view"),
    path("download", views.download, name="download"),
    path("reset", views.reset, name="reset"),
]