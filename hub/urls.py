from django.urls import path

from django.conf.urls import url
from django.views.generic import TemplateView

from . import views, md

app_name = 'hub'
urlpatterns = [
    path("", views.index, name="index"),
    path("post_create", views.PostCreate.as_view(), name="post_create"),
    path("post_create/<str:anchor>", views.PostCreate.as_view(), name="post_create"),
    path("post_update/<int:pk>", views.PostUpdate.as_view(), name="post_update"),
    path("post_delete/<int:id>", views.post_delete, name="post_delete"),

    url(r'^service-worker(.*.js)$',
        TemplateView.as_view(template_name='hub/service-worker.js',
            content_type='application/x-javascript')),

    path("md/<path:entry>", md.show_entry, name="show_enrty"),
]