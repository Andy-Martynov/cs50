from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

import json

from webpreview import web_preview
from webpreview import OpenGraph

import requests
from requests.exceptions import HTTPError

from account.models import User, Group, Membership
from folders.models import Folder, FolderShare
from .forms import LinksFolderForm, LinkForm
from .models import Link

PROXY = "https://cors-anywhere.herokuapp.com/";
PROXY = "http://alloworigin.com/get?url=";

@login_required
def index(request):
    return redirect(reverse('links:folder_list'))

def folder_delete(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    folder = Folder.objects.filter(id=pk).first()
    if not folder:
        messages.info(request, f"Delete, No {pk} folder", extra_tags='alert-warning')
        return redirect(reverse('links:folder_list'))
    folder.delete()
    return redirect(reverse('links:folder_list'))

def folder_detail(request, pk=None):
    parent = Folder.objects.filter(id=pk).first()
    folders = Folder.objects.filter(user=request.user, parent=parent, tag='links')
    shared = []
    shared_to_me = FolderShare.objects.filter(who=request.user)
    for share in shared_to_me:
        shared.append(share)
    i_share = FolderShare.objects.filter(folder__in=folders)
    groups = Group.objects.filter(creator=request.user)
    links = Link.objects.filter(folder=parent)
    return render(request, "links/folder_detail.html", {'object':parent, 'links':links, 'folder_tree':folders, 'shared':shared, 'i_share':i_share, 'groups':groups, })

def folder_list(request):
    folders = Folder.objects.filter(user=request.user, level=0, tag='links')
    shared = []
    shared_to_me = FolderShare.objects.filter(who=request.user)
    for share in shared_to_me:
        shared.append(share)
    i_share = FolderShare.objects.filter(folder__in=folders)
    groups = Group.objects.filter(creator=request.user)
    return render(request, "links/folder_list.html", {'folder_tree':folders, 'shared':shared, 'i_share':i_share, 'groups':groups, })

def folder_update(request, pk=None):
    folder = Folder.objects.filter(id=pk).first()
    if request.method == 'POST':
        form = LinksFolderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            folder.name = name
            folder.save()
            return redirect(reverse('links:folder_detail', kwargs={'pk': pk, }))
    form = LinksFolderForm(initial={'name': folder.name})
    return render(request, "folders/folder_form.html", {'form':form, })

def folder_create(request, parent_id=None):
    if request.method == 'POST':
        form = LinksFolderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            parent = None
            level=0
            if parent_id:
                parent = Folder.objects.filter(id=parent_id).first()
                if parent:
                    level = parent.level + 1
            Folder.objects.create(user=request.user, parent=parent, tag='links', name=name, level=level)
            if parent:
                return redirect(reverse('links:folder_detail', kwargs={'pk': parent_id, }))
            return redirect(reverse('links:folder_list'))
    form = LinksFolderForm()
    return render(request, "folders/folder_form.html", {'form':form, })

class LinkUpdate(LoginRequiredMixin, UpdateView) :
    model = Link
    form_class = LinkForm
    success_url = reverse_lazy('links:folder_list')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.success_url = reverse_lazy('links:folder_detail', kwargs={'pk': form.instance.folder.id})
        return super().form_valid(form)


def link_delete(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    link = Link.objects.filter(id=pk).first()
    if not link:
        messages.info(request, f"Delete, No {pk} link", extra_tags='alert-warning')
        return redirect(reverse('links:folder_list'))
    pk = link.folder.pk
    link.delete()
    return redirect(reverse('links:folder_detail', kwargs={'pk': pk}))


class LinkCreate(LoginRequiredMixin, CreateView) :
    model = Link
    form_class = LinkForm
    success_url = reverse_lazy('links:folder_list')

    def form_valid(self, form):
        if 'folder_id' in self.kwargs :
            folder_id = self.kwargs['folder_id']
            folder = Folder.objects.filter(id=folder_id).first()
            form.instance.folder = folder
            self.success_url = reverse_lazy('links:folder_detail', kwargs={'pk': folder.id})

            # response = None
            # headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.33"}
            # try:
            #     response = requests.get(form.instance.url)
            #     # If the response was successful, no Exception will be raised
            #     response.raise_for_status()
            # except HTTPError as http_err:
            #     errors = http_err
            # except Exception as err:
            #     errors = err
            # else:
            #     errors = 'Success!'
            # if response:
            #     if response.status_code == 200:
            #         title, description, image = web_preview(form.instance.url, headers=headers)
            #         form.instance.title = title
            #         form.instance.description = description
            #         form.instance.image = image
        return super().form_valid(form)

class LinkList(LoginRequiredMixin, ListView):
    model = Link





