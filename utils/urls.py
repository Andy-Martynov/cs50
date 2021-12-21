from django.urls import path

from . import views

app_name = 'utils'
urlpatterns = [
    path("album", views.album_files, name="album"),
    path("album/<str:mode>", views.album_files, name="album"),

    path("account", views.account_files, name="account"),
    path("account/<str:mode>", views.account_files, name="account"),
]