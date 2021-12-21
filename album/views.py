from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import os
from PIL import Image, ImageEnhance
import markdown2

from mysite import settings
from account.models import User
from .models import Album, Item, Extention, Animation
from .forms import ItemForm, AlbumForm, YouTubeForm, ExtentionForm

FOLDER_WIDTH = 240
FOLDER_HEIGHT = 180

# __________________________________________________ ALBUM VIEWS _______________

def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('album:user_albums', args=[request.user.id]))
    return redirect(reverse('album:user_albums'))

def owners(request):
    albums = Album.objects.filter(level=0, parent=None)
    owners = set()
    for album in albums :
        owners.add(album.user)
    return render(request, "album/owners.html", {"albums":albums, "owners":owners})

def user_albums(request, user_id=None):
    if user_id == None :
        user_id = request.user.id
    user = User.objects.filter(id=user_id).first()
    if user :
        albums = Album.objects.filter(user=user, level=0)
    else :
        albums = None # warning
    return render(request, "album/albums.html",
        {"this_album": None,
         "albums": albums,
         "owner":user,
         "min_w": int(FOLDER_WIDTH * 1.2),
         "min_h": int(FOLDER_HEIGHT * 1.2)})

def albums_tree(user, parent=None, mode=None):
    if not user:
        return None
    tree = []
    if not parent :
        albums = Album.objects.filter(user=user, level=0)
    else:
        albums = Album.objects.filter(parent=parent)
    for album in albums:
        childs = albums_tree(user, album)
        if mode:
            items = Item.objects.filter(album=album, mode=mode)
        else:
            items = Item.objects.filter(album=album)
        if len(childs) > 0 or items:
            tree.append(('A', album,))
            tree.extend(childs)
            for item in items:
                tree.append(('I', item, ))
    return tree

def user_links(request, user_id=None):
    if user_id == None :
        user_id = request.user.id
    user = User.objects.filter(id=user_id).first()
    tree = None
    if user :
        albums = Album.objects.filter(user=user).order_by('level')
        tree = albums_tree(user, parent=None, mode='LNK')
    else :
        albums = None # warning
    return render(request, "album/links.html",
        {"this_album": None,
         "albums": albums,
         'tree': tree,
         "owner":user,
         "min_w": int(FOLDER_WIDTH * 1.2),
         "min_h": int(FOLDER_HEIGHT * 1.2)})

def album_by_number(request, album_id) :
    album = Album.objects.filter(id=album_id).first()
    user = album.user

    albums = Album.objects.filter(parent=album)
    items = Item.objects.filter(album=album)

    return render(request, "album/items.html",
        {"this_album": album,
         "albums": albums,
         "items": items,
         "owner":user,
         "min_w": int(album.def_thumb_width * 1.2),
         "min_h": int(album.def_thumb_height * 1.2),
         "min_i_w": int(FOLDER_WIDTH * 1.2),
         "min_i_h": int(FOLDER_HEIGHT * 1.2)})

def show(request, id) :
    album = Album.objects.filter(id=id).first()
    if album :
        images = Item.objects.filter(album=album, mode='IMG')
        animations = Animation.objects.all()
        return render(request, "album/show.html", {"album":album, "images":images, "animations":animations})

@login_required
def album_delete(request, album_id) :
    album = Album.objects.filter(id=album_id).first()
    user_id = request.user.id
    if album :
        level = album.level
        if level > 0 :
            parent_id = album.parent.id
        else :
            user_id = album.user.id

        if (album.user == request.user) or request.user.is_superuser :
            album.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else's album", extra_tags='alert-danger')
    if level > 0 :
        return redirect(reverse('album:number', args=[parent_id]))
    else :
        return redirect(reverse('album:user_albums', args=[user_id]))

@login_required
def album_setup(request, id) :
    album = Album.objects.filter(id=id).first()
    user_id = request.user.id
    if album :
        level = album.level
        if level > 0 :
            parent_id = album.parent.id
        else :
            user_id = album.user.id

        thumb = album.thumb
        thumb_image = None
        if thumb :
            w = album.def_thumb_width
            h = album.def_thumb_height

            f = album.thumbfullname()
            try :
                thumb_image = Image.open(f)
            except :
                messages.info(request, f'open failed {f} >', extra_tags='alert-danger')
            if thumb_image :
                try :
                    thumb_image.thumbnail((w,h))
                except :
                    messages.info(request, f'Failed make thumbnail: {thumb_image}', extra_tags='alert-danger')
                try :
                    thumb_image = thumb_image.save(f)
                    messages.info(request, f'Thumb saved to {f}', extra_tags='alert-info')
                except :
                    messages.info(request, f'Failed save file: {f}', extra_tags='alert-danger')
            else :
                album.thumb = None
                album.save()
    if level > 0 :
        return redirect(reverse('album:number', args=[parent_id]))
    else :
        return redirect(reverse('album:user_albums', args=[user_id]))

class AlbumUpdate(LoginRequiredMixin, UpdateView) :
    model = Album
    form_class = AlbumForm

class AlbumCreate(LoginRequiredMixin, CreateView) :
    model = Album
    form_class = AlbumForm

    def form_valid(self, form):
        if 'album_id' in self.kwargs :
            album_id = self.kwargs['album_id']
            parent_album = Album.objects.filter(id=album_id).first();
            form.instance.parent = parent_album
            form.instance.level = parent_album.level + 1
            form.instance.user = parent_album.user
        else :
            form.instance.user = self.request.user
        return super().form_valid(form)


# class LinkFolderCreate(LoginRequiredMixin, CreateView) :
#     model = Album
#     form_class = LinkFolderForm
#     success_url = reverse_lazy('album:user_links')
#     template_name = 'album/link_folder_form.html'

#     def form_valid(self, form):
#         if 'album_id' in self.kwargs :
#             album_id = self.kwargs['album_id']
#             parent_album = Album.objects.filter(id=album_id).first();
#             form.instance.parent = parent_album
#             form.instance.level = parent_album.level + 1
#             form.instance.user = parent_album.user
#         else :
#             form.instance.user = self.request.user
#         return super().form_valid(form)

# __________________________________________________ ITEM VIEWS ________________

class ItemDetail(DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        image = self.object
        id = image.id
        album = image.album
        images = Item.objects.filter(album=album, mode='IMG')

        next = images.filter(id__gt=id).order_by('id').first()
        if not next :
            next = images.order_by('id').first()
        previous = images.filter(id__lt=id).order_by('id').last()
        if not previous :
            previous = images.order_by('id').last()
        context['next'] = next
        context['previous'] = previous
        context['first'] = images.order_by('id').first()
        context['last'] = images.order_by('id').last()
        return context


class ItemDetailInfo(DetailView):
    model = Item
    template_name = 'album/item_detail_info.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        image = self.object
        id = image.id
        album = image.album
        images = Item.objects.filter(album=album)

        next = images.filter(id__gt=id).order_by('id').first()
        if not next :
            next = images.order_by('id').first()
        previous = images.filter(id__lt=id).order_by('id').last()
        if not previous :
            previous = images.order_by('id').last()
        context['next'] = next
        context['previous'] = previous
        context['first'] = images.order_by('id').first()
        context['last'] = images.order_by('id').last()
        context['html'] = markdown2.markdown(image.text)
        return context

def unused(request, delete='no'):

    items = Item.objects.all()
    item_files = set()
    thumbs = set()
    dir = None
    for item in items:
        item_files.add(os.path.basename(item.file.name))
        dir = os.path.dirname(item.file.name)
        if item.thumb:
            thumbs.add(os.path.basename(item.thumb))

    context = {}
    context['item_files'] = item_files
    context['thumbs'] = thumbs

    if dir:
        files = set(os.listdir(os.path.join(settings.MEDIA_ROOT, dir)))
        context['files'] = files
        context['dir'] = dir
        context['path'] = os.path.join(settings.MEDIA_ROOT, dir)

    unusd = files.difference(item_files.union(thumbs))
    if delete == 'yes':
        for file in unusd:
            os.remove(os.path.join(settings.MEDIA_ROOT, dir, file))
        context['deleted'] = unusd
    else:
        context['unused'] = unusd

    return render(request, "album/unused.html", context)

@login_required
def item_delete(request, item_id) :
    item = Item.objects.filter(id=item_id).first()
    album_id = item.album.id
    if item :
        if (item.album.user == request.user) or request.user.is_superuser :
            item.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else'e item", extra_tags='alert-danger')
    return redirect(reverse('album:number', args=[album_id]))

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

@login_required
def item_setup(request, id) :
    item = Item.objects.filter(id=id).first()
    if item :
        file = item.file
        if file :
            ext = os.path.splitext(str(file))[1]
            folder = os.path.dirname(str(file))
            item_type = Extention.objects.filter(ext=ext).first()
            if item_type == None :
                messages.info(request, f"Unknown extention {ext}, if correct please add to Extention table", extra_tags='alert-warning')
                mode = 'UKN'
            else :
                mode = item_type.mode
            item.mode = mode

            album = item.album
            w = album.def_thumb_width
            h = album.def_thumb_height
            iw = album.max_image_width
            ih = album.max_image_height

            if mode == 'IMG' :
                f = item.file
                t = f'media/{folder}/thumb{id}.png'
                ff = f'media/{folder}/image{id}.png'
                thumb = None
                try :
                    thumb = Image.open(f)
                    image = Image.open(f)
                except :
                    messages.info(request, f'open failed, file: {folder} > {f} > {item.file} ', extra_tags='alert-danger')
                if thumb :
                    thumb.thumbnail((w,h))
                    image.thumbnail((iw,ih))
                    if item.album.watermark :
                        watermark = Image.open(item.album.watermark)
                        opacity = float(item.album.opacity)
                        interval = int(item.album.interval)
                        image = add_watermark(image, watermark, opacity=opacity, wm_interval=interval)
                    messages.info(request, f'Resize thumb to {w}x{h}, image to {iw}x{ih}', extra_tags='alert-info')
                    try :
                        thumb = thumb.save(t)
                        messages.info(request, f'Thumb saved to {t} folder {folder} ', extra_tags='alert-info')
                    except :
                        messages.info(request, f'Failed save file: {t} from {item.filefullname()}', extra_tags='alert-danger')
                    try :
                        image = image.save(ff)
                        messages.info(request, f'Image saved to {ff} folder {folder} ', extra_tags='alert-info')
                    except :
                        messages.info(request, f'Failed save file: {ff} from {item.filefullname()}', extra_tags='alert-danger')
                try :
                    item.thumb = '/' + t
                    item.file = f'{folder}/image{id}.png'
                    item.save()
                except :
                    messages.info(request, 'Could not save item', extra_tags='alert-danger')
            else :
                item.thumb = None
                item.save()
        return redirect(reverse('album:number', args=[item.album.id]))
    else :
        return redirect(reverse('album:user_albums'))

class ItemUpdate(LoginRequiredMixin, UpdateView) :
    model = Item
    form_class = ItemForm

class ItemCreate(LoginRequiredMixin, CreateView) :
    model = Item
    form_class = ItemForm
    # template_name = 'album/item_form.html'

    def form_valid(self, form):
        if 'album_id' in self.kwargs :
            album_id = self.kwargs['album_id']
            album = Album.objects.filter(id=album_id).first();
            form.instance.album = album
        return super().form_valid(form)

class YouTubeUpdate(LoginRequiredMixin, UpdateView) :
    model = Item
    form_class = YouTubeForm

class YouTubeCreate(LoginRequiredMixin, CreateView) :
    model = Item
    form_class = YouTubeForm

    def form_valid(self, form):
        if 'album_id' in self.kwargs :
            album_id = self.kwargs['album_id']
            album = Album.objects.filter(id=album_id).first();
            form.instance.album = album
            form.instance.mode = 'YTB'
        return super().form_valid(form)

# class LinkUpdate(LoginRequiredMixin, UpdateView) :
#     model = Item
#     form_class = LinkForm

# class LinkCreate(LoginRequiredMixin, CreateView) :
#     model = Item
#     form_class = LinkForm

#     def form_valid(self, form):
#         if 'album_id' in self.kwargs :
#             album_id = self.kwargs['album_id']
#             album = Album.objects.filter(id=album_id).first();
#             form.instance.album = album
#             form.instance.mode = 'LNK'
#         return super().form_valid(form)

# _____________________________________________ ANIMATION VIEWS ________________

# class AnimationUpdate(LoginRequiredMixin, UpdateView) :
#     model = Animation
#     form_class = AnimationForm

# class AnimationDelete(LoginRequiredMixin, DeleteView) :
#     model = Animation
#     success_url = reverse_lazy('album:animation_list')

# class AnimationCreate(LoginRequiredMixin, CreateView) :
#     model = Animation
#     form_class = AnimationForm

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)

# class AnimationList(LoginRequiredMixin, ListView) :
#     model = Animation

#     def get_queryset(self):
#         return Animation.objects.all().order_by('title')

# class AnimationDetail(LoginRequiredMixin, DetailView) :
#     model = Animation

# _____________________________________________ EXTENTION VIEWS ________________

class ExtentionUpdate(LoginRequiredMixin, UpdateView) :
    model = Extention
    form_class = ExtentionForm

class ExtentionDelete(LoginRequiredMixin, DeleteView) :
    model = Extention
    form_class = ExtentionForm

class ExtentionCreate(LoginRequiredMixin, CreateView) :
    model = Extention
    form_class = ExtentionForm

class ExtentionList(LoginRequiredMixin, ListView) :
    model = Extention

    def get_queryset(self):
        return Extention.objects.all().order_by('title')

class ExtentionDetail(LoginRequiredMixin, DetailView) :
    model = Extention







