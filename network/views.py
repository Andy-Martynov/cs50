from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import json

from account.models import User

from .models import Post, Follow, Like
from .forms import PostForm

def index(request):
    return redirect(reverse("network:post_create"))

@login_required
def post_list_filter(request, author='ALL') :
    return redirect(reverse('network:post_create', args=[author]))

class PostCreate(CreateView) :
    model = Post
    form_class = PostForm
    template_name = "network/post_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        posts = Post.objects.order_by('created').reverse().annotate(Count('like_me'))
        posts = posts.annotate(label=Count('like_me'))
        if self.request.user.is_authenticated :
            if 'author' in self.kwargs :
                author_username = self.kwargs['author']
                if author_username == 'FOLLOWING' :
                    context['filter'] = 'Following'
                    authors_i_follow = []
                    follows = Follow.objects.filter(who=self.request.user)
                    for follow in follows :
                        authors_i_follow.append(follow.whom)
                    posts = posts.filter(author__in=authors_i_follow)
            for post in posts :
                i_like = Like.objects.filter(post=post, who=self.request.user).first()
                if i_like :
                    post.label = 'Unlike'
                else :
                    post.label = 'Like'
                post.save()

        paginator = Paginator(posts, 10) # Show 10 per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['count'] = posts.count()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdate(UpdateView) :
    model = Post
    form_class = PostForm

@login_required
def user_profile(request, pk) :
    num_follow_i = None
    num_follow_me = None
    posts = Post.objects.order_by('created').reverse().annotate(Count('like_me'))
    posts = posts.annotate(label=Count('like_me'))
    author = User.objects.filter(id=pk).first()
    if author :
        posts = posts.filter(author=author)
        num_follow_i = author.follow_i.count()
        num_follow_me = author.follow_me.count()
        followers = []
        follows = Follow.objects.filter(whom=author)
        for follow in follows :
            followers.append(follow.who)
        authors_i_follow = []
        follows = Follow.objects.filter(who=author)
        for follow in follows :
            authors_i_follow.append(follow.whom)
        for post in posts :
            i_like = Like.objects.filter(post=post, who=request.user).first()
            if i_like :
                post.label = 'Unlike'
            else :
                post.label = 'Like'
            post.save()
    else :
        messages.info(request, "No user {pk}", extra_tags='alert-danger')
    paginator = Paginator(posts, 10) # Show 10 per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/user_profile.html',
                    {'page_obj': page_obj,
                     'author': author,
                     'num_follow_i': num_follow_i,
                     'num_follow_me': num_follow_me,
                     'followers': followers,
                     'authors_i_follow': authors_i_follow,
                     'count': posts.count()})

@login_required
def follow(request, pk) :
    author = User.objects.filter(id=pk).first()
    if author :
        follow = Follow.objects.filter(who=request.user, whom=author)
        if follow :
            follow.delete()
        else :
            Follow.objects.create(who=request.user, whom=author)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@csrf_exempt
@login_required
def like(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("post_id") is not None:
            post_id = data["post_id"]
            post = Post.objects.filter(id=post_id).first()
            if post :
                like = Like.objects.filter(who=request.user, post=post).first()
                if like :
                    like.delete()
                else :
                    Like.objects.create(who=request.user, post=post)
                return HttpResponse(status=204)
            return HttpResponse(status=402)
        return HttpResponse(status=401)
    else:
        return HttpResponse(status=400)

@csrf_exempt
@login_required
def edit(request):
    if request.method == 'PUT' :
        data = json.loads(request.body)
        if data.get("post_id") is not None:
            post_id = data["post_id"]
            post = Post.objects.filter(id=post_id).first()
            if post :
                if post.author == request.user : # ONLY OWN POST CAN BE EDITED
                    if data.get("text") is not None:
                        post.text = data["text"]
                        post.save()
                        return HttpResponse(status=204)
                    return HttpResponse(status=405)
                return HttpResponse(status=403)
            return HttpResponse(status=402)
        return HttpResponse(status=401)
    else:
        return HttpResponse(status=400)

