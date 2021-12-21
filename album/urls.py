from django.urls import path

from . import views

app_name = 'album'
urlpatterns = [
    path("", views.index, name="index"),

    path("owners", views.owners, name="owners"),

    path("unused", views.unused, name="unused"),
    path("unused/<str:delete>", views.unused, name="unused"),

    path("user_albums", views.user_albums, name="user_albums"),
    path("user_albums/<int:user_id>", views.user_albums, name="user_albums"),

    # path("user_links", views.user_links, name="user_links"),
    # path("user_links/<int:user_id>", views.user_links, name="user_links"),
    # path("link_folder_create", views.LinkFolderCreate.as_view(), name="link_folder_create"),

    path("number/<int:album_id>", views.album_by_number, name="number"),

    path("item_detail/<int:pk>", views.ItemDetail.as_view(), name="item_detail"),
    path("item_detail_info/<int:pk>", views.ItemDetailInfo.as_view(), name="item_detail_info"),

    path("item_create", views.ItemCreate.as_view(), name="item_create"),
    path("item_create/<int:album_id>", views.ItemCreate.as_view(), name="item_create"),

    path("item_update/<int:pk>", views.ItemUpdate.as_view(), name="item_update"),
    path("item_delete/<int:item_id>", views.item_delete, name="item_delete"),

    path("item_setup/<int:id>", views.item_setup, name="item_setup"),

    path("album_create", views.AlbumCreate.as_view(), name="album_create"),
    path("album_create/<int:album_id>", views.AlbumCreate.as_view(), name="album_create"),

    path("album_update/<int:pk>", views.AlbumUpdate.as_view(), name="album_update"),
    path("album_delete/<int:album_id>", views.album_delete, name="album_delete"),

    path("album_setup/<int:id>", views.album_setup, name="album_setup"),

    path("show/<int:id>", views.show, name="show"),

    path("youtube_create/<int:album_id>", views.YouTubeCreate.as_view(), name="youtube_create"),
    path("youtube_update/<int:pk>", views.YouTubeUpdate.as_view(), name="youtube_update"),

    # path("link_create/<int:album_id>", views.LinkCreate.as_view(), name="link_create"),
    # path("link_update/<int:pk>", views.LinkUpdate.as_view(), name="link_update"),

    # path("animation_create", views.AnimationCreate.as_view(), name="animation_create"),
    # path("animation_update/<int:pk>", views.AnimationUpdate.as_view(), name="animation_update"),
    # path("animation_delete/<int:pk>", views.AnimationDelete.as_view(), name="animation_delete"),
    # path("animation_detail/<int:pk>", views.AnimationDetail.as_view(), name="animation_detail"),
    # path("animation_list", views.AnimationList.as_view(), name="animation_list"),
]