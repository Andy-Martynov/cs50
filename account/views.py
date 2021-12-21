from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import random
from PIL import Image

from .models import User, Group, Membership
from .forms import UserForm, UserImageForm, GroupForm, PasswordResetEmailForm

from mysite import settings

def index(request) :
    return render(request, "hub/index.html")

class UserList(LoginRequiredMixin, ListView) :
    model = User
    template_name = 'account/user_list.html'

    def get_queryset(self):
        users = User.objects.order_by('username')
        list = []
        for user in users :
            item = {}
            item['user'] = user
            memberships = Membership.objects.filter(user=user)
            item['memberships'] = memberships
            list.append(item)
        return list

@login_required
def resize_260x260(request, id) :
    user = User.objects.filter(id=id).first()
    if user :
        f = settings.MEDIA_ROOT + user.imagefile()
        try :
            image = Image.open(f)
        except :
            messages.info(request, f'{f} open failed, MR: {settings.MEDIA_ROOT}', extra_tags='alert-danger')
        try:
            if image :
                image.thumbnail((260,260))
                image.save(f)
            else:
                messages.info(request, f'file {f} not found', extra_tags='alert-danger')
        except :
            messages.info(request, f'{f} resize failed', extra_tags='alert-danger')
        try :
            user.save()
        except :
            messages.info(request, 'WTF?', extra_tags='alert-danger')
    return redirect(reverse('hub:index'))

@login_required
def user_image_update(request, id=0) :
    if id == 0 :
        user = request.user
    else :
        user = User.objects.filter(id=id).first()
    if request.method == 'POST':
        form = UserImageForm(request.POST, request.FILES)
        if form.is_valid():
            user.image = form.cleaned_data['image']
            try :
                user.save()
            except :
                messages.info(request, 'WTF?', extra_tags='alert-danger')
            return redirect(reverse('account:resize_260x260', args=[user.id]))
    form = UserImageForm(initial={'username': user.username})
    return render(request, 'account/user_image_form.html', {'form': form, 'person': user})

@login_required
def user_update(request) :
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            try :
                request.user.save()
            except :
                messages.info(request, 'WTF?', extra_tags='alert-danger')
            # redirect to a new URL:
            return render(request, "hub/index.html")

    form = UserForm(initial={
        'username': request.user.username,
        'email': request.user.email,
        })
    return render(request, 'account/user_form.html', {'form': form})

# _________________________________________________ GROUP ______________________

class GroupList(LoginRequiredMixin, ListView) :
    model = Group

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        groups = Group.objects.all().annotate(Count('members'));
        if not self.request.user.is_superuser:
            groups = groups.filter(creator=self.request.user)

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
        context['group_list'] = group_list
        return context

class GroupDetail(LoginRequiredMixin, DetailView) :
    model = Group

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            group = Group.objects.filter(id=pk).first();

            users = User.objects.order_by('username')
            users = users.exclude(id=group.creator.id)

            memberships = Membership.objects.filter(group=group)
            count = memberships.count()
            members = []
            for membership in memberships :
                members.append(membership.user)
                users = users.exclude(id=membership.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['group'] = group
            context['users_not_in_group'] = users
        return context


class GroupCreate(LoginRequiredMixin, CreateView) :
    model = Group
    form_class = GroupForm
    # success_url = reverse('hub:index')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        users=User.objects.order_by('username')
        users = users.exclude(id=self.request.user.id)

        context['users'] = users
        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user
        self.success_url = reverse('account:group_list')
        return super().form_valid(form)


class GroupUpdate(LoginRequiredMixin, UpdateView) :
    model = Group
    form_class = GroupForm
    template_name = 'account/group_update_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            group = Group.objects.filter(id=pk).first();

            users=User.objects.order_by('username')
            users = users.exclude(id=group.creator.id)

            memberships = Membership.objects.filter(group=group)
            count = memberships.count()
            members = []
            for membership in memberships :
                members.append(membership.user)
                # users = users.exclude(id=membership.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['group'] = group
            context['users_not_in_group'] = users
        return context

    def form_valid(self, form):

        self.success_url = reverse('account:group_list') # self.request.META.get('HTTP_REFERER') #
        return super().form_valid(form)


@login_required
def group_delete(request, pk) :
    group = Group.objects.filter(id=pk).first()
    if group :
        if (group.creator == request.user) or request.user.is_superuser :
            group.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else'e group", extra_tags='alert-danger')
    # return redirect(reverse('hub:index'))
    return redirect(reverse('account:group_list'))

# _________________________________________________ MAIL _______________________

def mail_to(request, user_id=None, subj='cs50 mail', html='', text=''):
    if user_id:
        user = User.objects.filter(id=user_id).first()
        if user:
            sent = send_mail(
            subj,
            text,
            'andymartynovmail@gmail.com',
            [user.email],
            fail_silently=False,
            html_message = html,
            )
            return 200, sent
        return 404, f'user {user_id} not found'
    return 400, 'bad request, no user ID'

# _________________________________________________ LOGIN REGISTER LOGOUT ______

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None: # Check if authentication successful
            login(request, user)
            return redirect(reverse("hub:index"))
        return render(request, "account/login.html", {"message": "Invalid username and/or password."})
    return render(request, "account/login.html")

def guest_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("hub:index"))
    last = User.objects.all().last()
    username = f'Guest_{last.id + 1}'
    password = username
    email = 'nobody@nowhere.com'
    # Attempt to create new user
    try:
        user = User.objects.create_user(username, email, password)
        user.is_guest = True
        user.save()
    except IntegrityError:
        user = User.objects.filter(username=username).first()
        messages.info(request, f'User {username} already created', extra_tags='alert-warning')
    if user is not None: # Check if authentication successful
        messages.info(request, f'User {username} created', extra_tags='alert-warning')
        user = authenticate(username=username, password=password)
        login(request, user)
    return redirect(reverse("hub:index"))

def logout_view(request):
    user = request.user
    logout(request)
    if user.is_guest:
        user.delete()
    return redirect(reverse("hub:index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "account/register.html", {"message": "Passwords must match."})

        somebody = User.objects.filter(email=email, is_active=True).first()
        if somebody :
            return render(request, "account/register.html", {"message": f'{email} is already in use'})

        somebody = User.objects.filter(username=username, is_active=True).first()
        if somebody :
            return render(request, "account/register.html", {"message": f'The name "{username}" is already in use'})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            user = User.objects.filter(username=username).first()
            messages.info(request, f'User {username} already created, I am trying to send confirmation e-mail again.', extra_tags='alert-warning')

        login(request, user)
        user.is_active = False
        token = random.randint(0, 1000000)*1000+user.id
        user.token = token
        user.save()

        url = 'http://cs50.pythonanywhere.com/account/confirm/'+str(token)

        html = '''\
<div>
<h2>E-mail address confirmation</h2>
<br>
<p><a href="''' + url + '''"><button style="color: #ffffff; background-color: #000066; align: center;">PRESS TO CONFIRM</button></a></p>
<br>
<p>Thanks!</p>
</div>'''

        sent = send_mail(
        f'REGISTRATION {username} {email}',
        '',
        'andymartynovmail@gmail.com',
        [email],
        fail_silently=False,
        html_message = html,
        )

        logout(request)
        if sent == 0 :
            messages.info(request, f'Failed send confirmation email to "{email}"', extra_tags='alert-danger')
        else :
            messages.info(request, f'Confirmation email has been sent to {email}', extra_tags='alert-success')
        return redirect(reverse("hub:index"))
    return render(request, "account/register.html")

def confirm_email(request, token) :
    id = token % 1000
    user = User.objects.filter(id=id).first()
    if user :
        if user.token == token :
            user.is_active = True
            user.save()
            send_mail(
            f'{user.username} {user.email} registred',
            '',
            'andymartynovmail@gmail.com',
            ['andymartynovmail@gmail.com'],
            fail_silently=False,
            )
            login(request, user)
            messages.info(request, 'E-mail confirmed, thanks!', extra_tags='alert-success')
            return redirect(reverse("hub:index"))
        messages.info(request, 'Error, invalid token, e-mail confirmation failed.', extra_tags='alert-danger')
        return redirect(reverse("hub:index"))
    messages.info(request, f'Error, user {id} not found, e-mail confirmation failed.', extra_tags='alert-danger')
    return redirect(reverse("hub:index"))

# ______________________________________________________ PASSWORD RESET ________

def forgotten(request):
    if request.method == "POST":
        email = request.POST["email"]
        user = User.objects.filter(email=email).first()
        if not user :
            return render(request, "account/forgotten.html", {
                "message": f'{email} is not registred.'
            })

        token = random.randint(0, 1000000)*1000+user.id
        user.token = token
        user.save()
        reset_url = 'http://cs50.pythonanywhere.com/account/confirm_password_reset/'+str(token)
        html = '''\
<div>
<h2>PASSWORD RESET</h2>
<br>
<p>Do you really want to reset password to cs50.pythonanywhere.com?</p>
<p>Press "CONFIRM"<p>
<br>
<p>If you do not please delete this e-mail.</p>
<p><a href="''' + reset_url + '''"><button style="color: #ffffff; background-color: #000066; align: center;">CONFIRM</button></a></p>
<br>
<p>Thanks!</p>
</div>'''
        sent = send_mail(
        f'PASSWORD RESET {user.username}',
        '',
        'andymartynovmail@gmail.com',
        [email],
        fail_silently=False,
        html_message = html,
        )
        if sent == 0 :
            message = f'Something went wrong, the letter was not sent to {email}'
        else :
            message = f'Request was sent to {email}'
        return render(request, "account/forgotten.html", {"user_id": user.id, 'sent': (sent != 0), 'message': message})
    form = PasswordResetEmailForm()
    return render(request, 'account/forgotten.html', {'form': form})


def confirm_password_reset(request, token) :
    id = token % 1000
    user = User.objects.filter(id=id).first()
    if user :
        if user.token == token :
            context = {}
            context['user'] = user
            return render(request, 'account/password_reset.html', context)
        else:
            return HttpResponse(f'401_{id} {token}_{user.token} access denied') # invalid token
    else:
        return HttpResponse(f'400_{id} access denied')      # no user found

def password_reset(request, id):
    if request.method == "POST":
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation :
            return render(request, "account/password_reset.html", {
                "message": "Passwords do not match."
            })
        user = User.objects.filter(id=id).first()
        if not user :
            return render(request, "account/password_reset.html", {
                "message": f"User {id} not found."
            })
        user.set_password(password)
        user.save()
        messages.info(request, 'Password changed', extra_tags='alert-success')
        return redirect(reverse("hub:index"))
    return HttpResponse('WTF?!!')



