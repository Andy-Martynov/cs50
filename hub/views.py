from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Count
from django.views.generic.edit import CreateView,  UpdateView
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from network.models import Post, Like
from network.forms import PostForm
from todo.views import get_unread_task_shared_to_me

import os
from mysite import settings

#_______________________________________________________ INDEX _________________

def index(request):
    return redirect(reverse("hub:post_create"))


class PostCreate(CreateView) :
    model = Post
    form_class = PostForm
    template_name = "hub/index.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(comment=True).order_by('created').reverse().annotate(Count('like_me'))
        posts = posts.annotate(label=Count('like_me'))
        if self.request.user.is_authenticated :
            likes = Like.objects.filter(who=self.request.user)
            i_like = []
            for like in likes:
                i_like.append(like.post)
            context['i_like'] = i_like

        paginator = Paginator(posts, 10) # Show 10 per page.
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['count'] = posts.count()

        context['anchor'] = '#'
        context['kwargs'] = self.kwargs
        if 'anchor' in self.kwargs :
            context['anchor'] = self.kwargs['anchor']

        # Get new unrecieved tasks shared to me
        unrecieved_tasks, unrecieved_tasks_shares = get_unread_task_shared_to_me(self.request)
        context['unrecieved_tasks'] = unrecieved_tasks
        context['unrecieved_tasks_shares'] = unrecieved_tasks_shares

        certificates = os.listdir(path=os.path.join(settings.STATIC_ROOT, 'certificates'))
        certificates = list(map(lambda x: os.path.join('certificates', x), certificates))
        context['certificates'] = certificates

        # ['certificates/certificate_CS50AI.png', 'certificates/certificate_cs50w.png', 'certificates/cert_ibm.png']

        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.comment = True
        self.success_url = reverse("hub:post_create", kwargs={'anchor':'comments'})
        return super().form_valid(form)

class PostUpdate(UpdateView) :
    model = Post
    form_class = PostForm

@login_required
def post_delete(request, id=None):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if id:
                Post.objects.filter(id=id).delete()
    return redirect(reverse("hub:post_create"))



