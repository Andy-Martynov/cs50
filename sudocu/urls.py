from django.urls import path

from . import views

app_name = 'sudocu'
urlpatterns = [
    path("init", views.init, name="init"),
    path("empty", views.empty, name="empty"),
    path("start", views.start, name="start"),
    path("random/<int:n>", views.random_sudocu, name="random"),

    path("save/<str:name>", views.save, name="save"),
    path("load", views.load, name="load"),

    path("reduce", views.reduce, name="reduce"),
    path("path", views.path, name="path"),
    path("recursion", views.recursion, name="recursion"),

    path("show", views.show, name="show"),
    path("show/<str:mode>", views.show, name="show"),

    path("ai_move", views.ai_move, name="ai_move"),
    path("ai_move/<str:mode>", views.ai_move, name="ai_move"),

    path("move/<int:r>/<int:c>/<int:v>", views.move, name="move"),
]