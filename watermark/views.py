from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

import os
from PIL import Image, ImageEnhance

from mysite import settings
from .forms import WatermarkUploadForm

IMAGES_FOLDER = os.path.join(settings.MEDIA_ROOT, 'watermark', 'images')
WATERMARKS_FOLDER = os.path.join(settings.MEDIA_ROOT, 'watermark', 'watermarks')
RESULTS_FOLDER = os.path.join(settings.MEDIA_ROOT, 'watermark', 'result')

IMAGES_URL = os.path.join(settings.MEDIA_URL, 'watermark', 'images')
WATERMARKS_URL = os.path.join(settings.MEDIA_URL, 'watermark', 'watermarks')
RESULTS_URL = os.path.join(settings.MEDIA_URL, 'watermark', 'result')

def index(request, opacity=1, interval=300) :
    images = []
    image_files = os.listdir(IMAGES_FOLDER)
    for file in image_files :
        images.append(os.path.join(IMAGES_URL, file))

    watermark = os.path.join(WATERMARKS_URL, os.listdir(WATERMARKS_FOLDER)[0])

    return render(request, "watermark/index.html", {'images':images, 'watermark':watermark})

def load(request):
    if request.method == 'POST':
        form = WatermarkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_files = os.listdir(IMAGES_FOLDER)
            for file in image_files :
                os.remove(os.path.join(IMAGES_FOLDER, file))
            watermark_files = os.listdir(WATERMARKS_FOLDER)
            for file in watermark_files :
                os.remove(os.path.join(WATERMARKS_FOLDER, file))
            result_files = os.listdir(RESULTS_FOLDER)
            for file in result_files :
                os.remove(os.path.join(RESULTS_FOLDER, file))

            files = request.FILES.getlist("files")
            watermark = request.FILES['watermark']

            fs = FileSystemStorage()

            fn = os.path.join(WATERMARKS_FOLDER, watermark.name)
            if fs.exists(fn) :
                fs.delete(fn)
            fs.save(fn, watermark)

            for file in files :
                fn = os.path.join(IMAGES_FOLDER, file.name)
                if fs.exists(fn) :
                    fs.delete(fn)
                fs.save(fn, file)

                messages.info(request, f'file: {file}, watermark: {watermark}', extra_tags='alert-info')
        return redirect(reverse('watermark:index'))
    else:
        form = WatermarkUploadForm()
    return render(request, 'watermark/upload.html', {'form': form})

def add_watermark(image, watermark, opacity=1, wm_interval=0):
    assert opacity >= 0 and opacity <= 1
    if opacity < 1:
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        else:
            watermark = watermark.copy()
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    for y in range(0, image.size[1], watermark.size[1]+wm_interval):
        for x in range(0, image.size[0], watermark.size[0]+wm_interval):
            layer.paste(watermark, (x, y))
    return Image.composite(layer,  image,  layer)

def view(request, name=None, opacity='0.5', interval=300) :
    image = None
    image = Image.open(os.path.join(IMAGES_FOLDER, name))
    watermark = Image.open(os.path.join(WATERMARKS_FOLDER, os.listdir(WATERMARKS_FOLDER)[0]))
    image = add_watermark(image, watermark, opacity=float(opacity), wm_interval=interval)
    image.save(os.path.join(RESULTS_FOLDER, name))
    src = os.path.join(RESULTS_URL, name)
    return render(request, "watermark/view.html", {'src':src,'name':name, 'opacity':opacity, 'interval':interval})

def download(request, opacity='0.5', interval=300) :
    result_files = os.listdir(RESULTS_FOLDER)
    for file in result_files :
        os.remove(os.path.join(RESULTS_FOLDER, file))
    watermark = Image.open(os.path.join(WATERMARKS_FOLDER, os.listdir(WATERMARKS_FOLDER)[0]))

    srcs = []
    image_files = os.listdir(IMAGES_FOLDER)
    for name in image_files :
        image = Image.open(os.path.join(IMAGES_FOLDER, name))
        image = add_watermark(image, watermark, opacity=float(opacity), wm_interval=interval)
        image.save(os.path.join(RESULTS_FOLDER, name))
        src = os.path.join(RESULTS_URL, name)
        srcs.append(src)
    return render(request, "watermark/download.html", {'srcs':srcs})

def reset(request):
    image_files = os.listdir(IMAGES_FOLDER)
    for file in image_files :
        os.remove(os.path.join(IMAGES_FOLDER, file))
    watermark_files = os.listdir(WATERMARKS_FOLDER)
    for file in watermark_files :
        os.remove(os.path.join(WATERMARKS_FOLDER, file))
    result_files = os.listdir(RESULTS_FOLDER)
    for file in result_files :
        os.remove(os.path.join(RESULTS_FOLDER, file))
    return render(request, 'watermark/reset.html')


