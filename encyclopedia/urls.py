from django.urls import path

from . import views

app_name = 'encyclopedia'
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.show_entry, name="show_entry"),
    path("search", views.search, name="search"),
    path("new", views.new_entry, name="new_entry"),
    path("edit", views.edit_entry, name="edit_entry"),
    path("random", views.random_entry, name="random_entry"),
]
