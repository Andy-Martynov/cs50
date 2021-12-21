
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
from django.template.loader import render_to_string

import json

from account.models import User, Group, Membership
from .models import Task, Share
from .forms import TaskForm
from account.views import mail_to

from rtc.views import pusher_client

# import pusher

# pusher_client = pusher.Pusher(
#   app_id='1152832',
#   key='bbe70803665a7a964619',
#   secret='541db5cfad7af600f737',
#   cluster='eu',
#   ssl=True
# )

@login_required
def index(request):
    return redirect(reverse('todo:task_list'))

def task_tree(user=None, parent=None, task=None):
    tree = []
    if task:
        tree.append(task)
        childs = task_tree(parent=task)
        tree.extend(childs)
        return tree
    if not parent :
        root = Task.objects.filter(level=0, user=user, prev=None).first()
    else:
        root = Task.objects.filter(parent=parent, prev=None).first()
    while root:
        tree.append(root)
        childs = task_tree(user, root)
        tree.extend(childs)
        root = root.next
    return tree

@csrf_exempt
@login_required
def check(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("task_id") is not None:
            task_id = data["task_id"]
            task = Task.objects.filter(id=task_id).first()
            if task :
                task.checked = not task.checked;
                task.save()

                data = {}
                data['username'] = request.user.username
                data['user_id'] = request.user.id
                data['task_id'] = task.id
                data['checked'] = task.checked

                pusher_client.trigger('my-channel', 'todo_task_toggle_checked', data)

                return HttpResponse(status=200)
            return HttpResponse(status=404)
        return HttpResponse(status=400)
    else:
        return HttpResponse(status=401)

@csrf_exempt
@login_required
def add_share(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("task_id") is not None:
            task_id = data["task_id"]
            task = Task.objects.filter(id=task_id).first()
            if task :
                if data.get("user_id") is not None:
                    user_id = data["user_id"]
                    user = User.objects.filter(id=user_id).first()
                    if user :
                        if user != task.user:
                            share = Share.objects.filter(task=task, who=user).first()
                            if not share:
                                Share.objects.create(task=task, who=user)
                                return HttpResponse(status=200)
                            return HttpResponse(status=201)
                        return HttpResponse(status=202)
                    return HttpResponse(status=404)
                return HttpResponse(status=400)
            return HttpResponse(status=414)
        return HttpResponse(status=410)
    else:
        return HttpResponse(status=401)

@csrf_exempt
@login_required
def remove_share(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("task_id") is not None:
            task_id = data["task_id"]
            task = Task.objects.filter(id=task_id).first()
            if task :
                if data.get("user_id") is not None:
                    user_id = data["user_id"]
                    user = User.objects.filter(id=user_id).first()
                    if user :
                        if user != task.user:
                            share = Share.objects.filter(task=task, who=user).first()
                            if share:
                                share.delete()
                                return HttpResponse(status=200)
                            return HttpResponse(status=201)
                        return HttpResponse(status=202)
                    return HttpResponse(status=404)
                return HttpResponse(status=400)
            return HttpResponse(status=414)
        return HttpResponse(status=410)
    else:
        return HttpResponse(status=401)

def add_subtasks(task, text):
    if not (task and text):
        return False
    last_task = Task.objects.filter(parent=task, next=None).first()
    text = text.replace('\r\n', '\n')
    lines = text.split('\n')
    first_task = None
    current_task = None
    for line in lines:
        new_task = Task.objects.create(parent=task, user=task.user, name=line, prev=current_task, level=task.level+1)
        if not first_task:
            first_task = new_task
            if last_task:
                last_task.next = first_task
                last_task.save()
        if  current_task:
            current_task.next = new_task
            new_task.prev = current_task
            current_task.save()
            new_task.save()
        current_task = new_task
    return True


class TaskUpdate(LoginRequiredMixin, UpdateView) :
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('todo:task_list')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['task_tree'] = task_tree(user=self.request.user, parent=self.object)
        context['update'] = True
        return context

    def form_valid(self, form):
        form.instance.save()
        ok = add_subtasks(form.instance, form.instance.todo)
        if not ok:
            messages.info(self.request, "Something went wrong while adding todo list", extra_tags='alert-warning')
        form.instance.todo = None
        return super().form_valid(form)


def task_delete(request, pk=None):
    if not pk:
        messages.info(request, "Delete, No ID", extra_tags='alert-warning')
    task = Task.objects.filter(id=pk).first()
    if not task:
        messages.info(request, f"Delete, No {pk} task", extra_tags='alert-warning')
        return redirect(reverse('todo:task_list'))
    prev = task.prev
    next = task.next
    if prev:
        prev.next = next
        if next:
            next.prev = prev
        prev.save()
    if next:
        next.prev = prev
        if prev:
            prev.next = next
        next.save()
    task.delete()
    return redirect(reverse('todo:task_list'))

def reminder(request, share_id, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        share = Share.objects.filter(id=share_id).first()
        if share:
            html = render_to_string("todo/reminder.html", {'share':share})
            status, message = mail_to(request,
                    user_id=user_id,
                    subj=f'Task reminder from {request.user}',
                    html=html,
                    text=f'{share.who} shared task for you,\r\n\r\n{share.task}\r\n\r\n see on https://cs50.pythonanywhere.com/todo/detail/{share.task.id}')
            if status == 200:
                share.sent = True
                return HttpResponse(status=200)
            return HttpResponse(status=500)
        return HttpResponse(status=404)
    return HttpResponse(status=405)

def preview(request, share_id):
    share = Share.objects.filter(id=share_id).first()
    return render(request, "todo/reminder.html", {'share':share})

def task_share(request, pk=None):
    if not pk:
        messages.info(request, "Share, No ID", extra_tags='alert-warning')
    task = Task.objects.filter(id=pk).first()
    if not task:
        messages.info(request, f"Share, No {pk} task", extra_tags='alert-warning')
        return redirect(reverse('todo:task_list'))
    groups = Group.objects.all().annotate(Count('members'))
    groups = groups.filter(creator=request.user)
    group_list = []
    for group in groups :
        item = {}
        item['group'] = group
        memberships = Membership.objects.filter(group=group)
        count = memberships.count()
        item['count'] = count
        members = []
        for membership in memberships :
            members.append(membership.user)
        item['members'] = members
        group_list.append(item)
    shared = []
    shares = Share.objects.filter(task=task)
    for share in shares:
        shared.append(share.who)
    return render(request, "todo/task_share.html", {'task': task, 'group_list': group_list, 'shared': shared})


class TaskCreate(LoginRequiredMixin, CreateView) :
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('todo:task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.save()

        if 'parent_id' in self.kwargs :
            parent_id = self.kwargs['parent_id']
            parent = Task.objects.filter(id=parent_id).first()
            form.instance.parent = parent
            form.instance.user = parent.user
            form.instance.level = parent.level + 1

            prev = Task.objects.filter(parent=parent, next=None).first()
            if prev:
                prev.next = form.instance
                prev.save()
            form.instance.prev = prev
        elif 'link_id' in self.kwargs :
            link_id = self.kwargs['link_id']
            mode = self.kwargs['mode']
            link = Task.objects.filter(id=link_id).first()
            parent = link.parent
            form.instance.user = link.user
            form.instance.parent = parent
            if parent:
                form.instance.level = parent.level + 1

            if mode == 'after':
                form.instance.prev = link
                form.instance.next = link.next
                if link.next:
                    link.next.prev = form.instance
                    link.next.save()
                link.next = form.instance
                link.save()
            else:
                form.instance.prev = link.prev
                form.instance.next = link
                if link.prev:
                    link.prev.next = form.instance
                    link.prev.save()
                link.prev = form.instance
                link.save()
        else: # New level 0 task
            form.instance.user = self.request.user
            prev = Task.objects.filter(level=0, next=None, user=self.request.user).first()
            if prev:
                if prev != form.instance:
                    prev.next = form.instance
                    prev.save()
            if prev != form.instance:
                form.instance.prev = prev
        if form.instance.todo:
            ok = add_subtasks(form.instance, form.instance.todo)
        if not ok:
            messages.info(self.request, "Something went wrong while adding todo list", extra_tags='alert-warning')
        form.instance.todo = None
        return super().form_valid(form)


class TaskList(LoginRequiredMixin, ListView) :
    model = Task

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        my_tasks = task_tree(user=self.request.user)
        context['task_tree'] = my_tasks

        shared = []
        shared_to_me = Share.objects.filter(who=self.request.user)
        for share in shared_to_me:
            shared.append(task_tree(task=share.task))
        context['shared'] = shared
        context['shared_to_me'] = shared_to_me


        i_share = Share.objects.filter(task__in=my_tasks)
        context['i_share'] = i_share

        context['groups'] = Group.objects.filter(creator=self.request.user)
        return context

class TaskDetail(LoginRequiredMixin, DetailView) :
    model = Task

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['task_tree'] = task_tree(user=self.request.user, parent=self.object)
        return context

def get_unread_task_shared_to_me(request) :
    tasks = None
    unread_shared_to_me = None
    if request.user.is_authenticated:
        unread_shared_to_me = Share.objects.filter(who=request.user, recieved=False)
        tasks = []
        for share in unread_shared_to_me:
            tasks.append(share.task)
    return tasks, unread_shared_to_me

def recieve(request, share_id):
    share = Share.objects.filter(id=share_id).first()
    if share:
        share.recieved = True
        share.save()
        return HttpResponse(status=200)
    return HttpResponse(status=404)

def accept(request, share_id):
    share = Share.objects.filter(id=share_id).first()
    if share:
        share.accepted = True
        share.rejected = False
        share.recieved = True
        share.save()
        return HttpResponse(status=200)
    return HttpResponse(status=404)

def reject(request, share_id):
    share = Share.objects.filter(id=share_id).first()
    if share:
        share.accepted = False
        share.rejected = True
        share.recieved = True
        share.save()
        return HttpResponse(status=200)
    return HttpResponse(status=404)






































