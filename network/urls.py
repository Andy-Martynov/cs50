from django.urls import path

from . import views

app_name = 'network'
urlpatterns = [
    path("", views.index, name="index"),

    path("post_create", views.PostCreate.as_view(), name="post_create"),
    path("post_create/<str:author>", views.PostCreate.as_view(), name="post_create"),
    path("post_update/<int:pk>", views.PostUpdate.as_view(), name="post_update"),
    # path("post_list", views.PostList.as_view(), name="post_list"),
    # path("post_list/<str:author>/<str:mode>", views.PostList.as_view(), name="post_list"),

    path("filter", views.post_list_filter, name="filter"),
    path("filter/<str:author>", views.post_list_filter, name="filter"),
    # path("filter/<str:author>/<str:mode>", views.post_list_filter, name="filter"),

    path("user_profile/<int:pk>", views.user_profile, name="user_profile"),

    path("follow/<int:pk>", views.follow, name="follow"),
    path("like", views.like, name="like"),
    path("edit", views.edit, name="edit"),
]
