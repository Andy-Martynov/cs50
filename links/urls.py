from django.urls import path
from . import views

app_name = 'links'
urlpatterns = [
    path("", views.index, name="index"),

    path("folder_list", views.folder_list, name="folder_list"),

    path("folder_create", views.folder_create, name="folder_create"),
    path("folder_create/<int:parent_id>", views.folder_create, name="folder_create"),

    path("folder_detail/<int:pk>", views.folder_detail, name="folder_detail"),
    path("folder_update/<int:pk>", views.folder_update, name="folder_update"),
    path("folder_delete/<int:pk>", views.folder_delete, name="folder_delete"),

    path("list", views.LinkList.as_view(), name="link_list"),
    path("create/<int:folder_id>", views.LinkCreate.as_view(), name="link_create"),
    path("update/<int:pk>", views.LinkUpdate.as_view(), name="link_update"),
    path("delete/<int:pk>", views.link_delete, name="link_delete"),
]