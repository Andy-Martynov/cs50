from django.shortcuts import render


def index(request):
    return render(request, "project0/index.html")

def languages(request):
    return render(request, "project0/languages.html")

def poetry(request):
    return render(request, "project0/poetry.html")

def photos(request):
    return render(request, "project0/photos.html")



