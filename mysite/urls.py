"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("hub.urls")),
    path("account/", include("account.urls")),
    path("rtc/", include("rtc.urls")),
    path("mail/", include("mail.urls")),
    path("game/", include("game.urls")),
    path("othello/", include("othello.urls")),
    path("connect4/", include("connect4.urls")),
    path("four/", include("four.urls")),
    path("auctions/", include("auctions.urls")),
    path("wiki/", include("encyclopedia.urls")),
    path("network/", include("network.urls")),
    path("meeting/", include("meeting.urls")),
    path("sudocu/", include("sudocu.urls")),
    path("album/", include("album.urls")),
    path("watermark/", include("watermark.urls")),
    path("animation/", include("animation.urls")),
    path("utils/", include("utils.urls")),
    path("project0/", include("project0.urls")),
    path("learn/", include("learn.urls")),
    path("todo/", include("todo.urls")),
    path("links/", include("links.urls")),
    path("folders/", include("folders.urls")),
    path("chat/", include("chat.urls")),
    path("explorer/", include("explorer.urls")),
    path("adminboard/", include("adminboard.urls")),
    path("currency/", include("currency.urls")),
]
