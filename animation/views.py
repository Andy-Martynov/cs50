from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import os

from mysite import settings
from account.models import User
from album.models import Animation
from .forms import AnimationForm

def index(request):
    return render(request, "animation/index.html")

# _____________________________________________ ANIMATION VIEWS ________________

class AnimationPreview(UpdateView) :
    model = Animation
    form_class = AnimationForm
    template_name = 'animation/animation_detail_form.html'

    def form_valid(self, form):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        form.instance.session_key = self.request.session.session_key
        form.instance.save()
        self.success_url = reverse('animation:animation_detail', args=[form.instance.id])
        messages.info(self.request, "ANIMAtIoN SAVED", extra_tags='alert-warning')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        context['session_key'] = self.request.session.session_key
        return context


class AnimationDelete(DeleteView) :
    model = Animation
    success_url = reverse_lazy('animation:animation_list')

class AnimationCreate(CreateView) :
    model = Animation
    form_class = AnimationForm
    template_name = 'animation/animation_detail_form.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user

        form.instance.session_key = self.request.session.session_key
        form.instance.save()
        self.success_url = reverse('animation:animation_detail', args=[form.instance.id])
        return super().form_valid(form)

class AnimationList(ListView) :
    model = Animation
    template_name = 'animation/animation_list.html'

    def get_queryset(self):
        return Animation.objects.all().order_by('user', 'title')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        context['session_key'] = self.request.session.session_key
        return context


def animation_clone(request, pk) :
    if not request.session.exists(request.session.session_key):
        request.session.create()

    source = Animation.objects.filter(id=pk).first()
    if source :
        title = source.title + '_clone'

        clone = Animation.objects.filter(title=title, session_key=request.session.session_key).first()
        if clone:
            messages.info(request, f"You already have '{title}' animation", extra_tags='alert-warning')
            return redirect(reverse('animation:animation_detail', args=[clone.id]))

        clone = Animation.objects.create(title=title)
        clone.prefix = source.prefix
        clone.duration = source.duration
        clone.delay = source.delay
        clone.count = source.count
        clone.direction = source.direction
        clone.timing = source.timing
        clone.fill = source.fill
        clone.keyframes = source.keyframes
        if request.user.is_authenticated :
            clone.user = request.user

        if request.session.get('animation_title', False):
            request.session['animation_title'] = request.session.get('animation_title') + ' ' + clone.title
        else:
            request.session['animation_title'] = clone.title

        clone.session_key = request.session.session_key
        clone.save()
    return redirect(reverse('animation:animation_detail', args=[clone.id]))


class AnimationCopy(DetailView) :
    model = Animation
    template_name = 'animation/animation_copy.html'



