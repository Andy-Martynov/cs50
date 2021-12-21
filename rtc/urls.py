from django.urls import path

# from django.conf.urls import url
# from django.views.generic import TemplateView

from . import views

app_name = 'rtc'
urlpatterns = [
    path("", views.index, name="index"),

    path('auth', views.pusher_auth, name='pusher_auth'),

    path("hello/<str:text>", views.hello, name="hello"),
    path("test", views.test, name="test"),
    path("trigger", views.trigger, name="trigger"),

    path('beams-auth', views.pusher_beams_auth, name='pusher_beams_auth'),
    path('beams-auth/<int:user_id>', views.pusher_beams_auth, name='pusher_beams_auth'),
    path("beam_hello", views.beam_hello, name="beam_hello"),
    path("beam_hello/<str:text>", views.beam_hello, name="beam_hello"),
    path("beam_user_message/<int:id>", views.beam_user_message, name="beam_user_message"),
]
