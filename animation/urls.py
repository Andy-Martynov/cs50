from django.urls import path

from . import views

app_name = 'animation'
urlpatterns = [
    path("", views.index, name="index"),

    path("animation_create", views.AnimationCreate.as_view(), name="animation_create"),
    # path("animation_update/<int:pk>", views.AnimationUpdate.as_view(), name="animation_update"),
    path("animation_clone/<int:pk>", views.animation_clone, name="animation_clone"),
    path("animation_delete/<int:pk>", views.AnimationDelete.as_view(), name="animation_delete"),
    path("animation_detail/<int:pk>", views.AnimationPreview.as_view(), name="animation_detail"),
    path("animation_list", views.AnimationList.as_view(), name="animation_list"),
    path("animation_copy/<int:pk>", views.AnimationCopy.as_view(), name="animation_copy"),

]