from django.urls import path

from . import views, api

app_name='account'
urlpatterns = [
    path("", views.index, name="index"),

    path("list", views.UserList.as_view(), name="user_list"),
    path("update", views.user_update, name="user_update"),
    path("image_update", views.user_image_update, name="user_image_update"),
    path("image_update/<int:id>/", views.user_image_update, name="user_image_update"),

    path("group_list", views.GroupList.as_view(), name="group_list"),
    path("group_detail/<int:pk>", views.GroupDetail.as_view(), name="group_detail"),
    path("group_create", views.GroupCreate.as_view(), name="group_create"),
    path("group_update/<int:pk>", views.GroupUpdate.as_view(), name="group_update"),
    path("group_delete/<int:pk>", views.group_delete, name="group_delete"),

    path("resize_260x260/<int:id>", views.resize_260x260, name="resize_260x260"),

    path("confirm/<int:token>", views.confirm_email, name="confirm"),

    path("login", views.login_view, name="login"),
    path("guest_login", views.guest_login, name="guest_login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("forgotten", views.forgotten, name="forgotten"),
    path("confirm_password_reset/<int:token>", views.confirm_password_reset, name="confirm_password_reset"),
    path("password_reset/<int:id>", views.password_reset, name="password_reset"),

    path("user_info/<int:id>", api.user_info, name="user_info"),
    path("group_info/<int:id>", api.group_info, name="group_info"),
]