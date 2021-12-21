from django.urls import path

from . import views

app_name = 'learn'
urlpatterns = [
    path("", views.index, name="index"),

    path("four_plots", views.four_plots, name="four_plots"),

    path("k_means", views.k_means, name="k_means"),
    path("k_means_step", views.k_means_step, name="k_means_step"),
    path("k_means_3d", views.k_means_3d, name="k_means_3d"),
    path("k_means_3d_step", views.k_means_3d_step, name="k_means_3d_step"),

    path("classification", views.classification, name="classification"),
    path("classification/<str:delta>", views.classification, name="classification"),
    path("nnc", views.nnc, name="nnc"),
    path("nnc/<int:k>", views.nnc, name="nnc"),
    path("perceptron", views.perceptron, name="perceptron"),
    path("perceptron/<str:alpha>", views.perceptron, name="perceptron"),
    path("perceptron/<str:alpha>/<str:gamma>", views.perceptron, name="perceptron"),
]
