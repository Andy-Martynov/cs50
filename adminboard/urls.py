from django.urls import path

from . import views

app_name='adminboard'
urlpatterns = [
    path("", views.index, name="index"),

    path("db_clean", views.db_clean, name="db_clean"),

    path("files", views.files, name="files"),
    path("files/<str:folder>", views.files, name="files"),

    # path("list", views.UserList.as_view(), name="user_list"),
    # path("update", views.user_update, name="user_update"),
    # path("image_update", views.user_image_update, name="user_image_update"),
    # path("image_update/<int:id>/", views.user_image_update, name="user_image_update"),

]