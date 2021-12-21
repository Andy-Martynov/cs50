from django.urls import path

from . import views

app_name = 'explorer'
urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),

    path("load_dataset", views.load_dataset, name="load_dataset"),
    path("load_dataset/<str:mode>", views.load_dataset, name="load_dataset"),
    path("set_param", views.set_param, name="set_param"),

    path("column_info/<str:dfname>/<str:cname>", views.column_info, name="column_info"),
    path("mi_scores", views.mi_scores, name="mi_scores"),
    path("correlation", views.correlation, name="correlation"),
    path("get_outliers", views.get_outliers, name="get_outliers"),
]
