# from django.contrib.auth import authenticate, login, logout
# from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse

import json
import random
from decimal import Decimal
from PIL import Image

center_latitude = 55.394290
center_longitude = 37.624031
center_radius = 1

radius = 0.01

from account.models import User, Group, Membership
from .models import Location, Meeting, Participation
from .forms import LocationForm, MeetingForm

# ___________________________________________________ MAP VIEWS ________________

def svg_marker(width=24, height=24, stroke='white', fill='#1b468d', x=1, y=1, w=22, h=22, textx=2, texty=18, size=12, family='Courier', weight='bold', anchor='left', fill2='yellow', text='U') :
    m =  f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"> '
    m += f'<rect stroke="{stroke}" fill="{fill}" x="{x}" y="{y}" width="{w}" height="{h}" /> '
    m += f'<text x="{textx}" y="{texty}" font-size="{size}pt" font-family="{family}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill2}">{text}</text></svg>'
    return m

def marker(name, color='#1b468d') :
    l = len(name)
    s = 12
    w = s*0.72*l+22
    m = svg_marker(width=w, height=s+12, stroke='white', fill=color, x=1, y=7, w=w-2, h=s+7, textx=4, texty=s+7, size=s, family='Courier', weight='bold', anchor='left', fill2='yellow', text=name)
    return m

def coords(user) :
    c = {}
    # c['latitude'] = center_latitude + center_radius * (2 * random.random() -1)
    # c['longitude'] = center_longitude + center_radius * (2 * random.random() -1)
    c['latitude'] = user.latitude + radius * (2 * random.random() - radius)
    c['longitude'] = user.longitude + radius * (2 * random.random() - radius)
    return c

# __________________________________________________ VIEWS _____________________

def index(request):
    if request.user.is_authenticated :
        return render(request, "meeting/index_logged_in.html")
    return render(request, "meeting/index.html")

@login_required
def map(request):
    locations = Location.objects.all()
    groups = Group.objects.all()
    users = User.objects.all()
    meetings = Meeting.objects.all()
    return render(request, "meeting/map.html",
                    {'locations': locations,
                     'groups': groups,
                     'users' : users,
                     'meetings': meetings,
                    })

@login_required
def location(request):
    return render(request, "meeting/location.html")

@login_required
def set_tags_markers_all(request) :
    users = User.objects.all()
    for user in users :
        user.tag = user.username[0:3]
        user.marker = marker(text=user.username, size=7, width=len(user.username)*10, w=len(user.username)*10-2)
        user.save()
    return HttpResponse(200)

# _____________________________________________________ MAP API ________________

@csrf_exempt
@login_required
def set_coords(request):
    if request.method == 'POST' :
        data = json.loads(request.body)
        if data.get("latitude") is not None:
            request.user.latitude = data["latitude"]
            if data.get("longitude") is not None:
                request.user.longitude = data["longitude"]
                try :
                    request.user.save()
                    return HttpResponse(status=200)
                except :
                    return HttpResponse(status=403)
            else :
                return HttpResponse(status=402)
        else :
            return HttpResponse(status=401)
    else:
        return HttpResponse(status=400)

@login_required
def user_info(request, id):
    user = User.objects.filter(id=id).first()
    if user :
        return JsonResponse(user.serialize(), safe=False, status=200)
    else :
        return JsonResponse('user not found', safe=False, status=404)

@login_required
def location_info(request, id):
    location = Location.objects.filter(id=id).first()
    if location :
        return JsonResponse(location.serialize(), safe=False, status=200)
    else :
        return JsonResponse('location not found', safe=False, status=404)

@login_required
def group_info(request, id):
    group = Group.objects.filter(id=id).first()
    if group :
        memberships = Membership.objects.filter(group=group)
        members = []
        for membership in memberships :
            members.append(membership.user)
        for user in members :
            user.marker = marker(user.username, color='#660000')
            user.save()
        return JsonResponse([user.serialize() for user in members], safe=False)
    else :
        return JsonResponse(f'group {id} not found', safe=False, status=404)

@login_required
def meeting_info(request, id):
    meeting = Meeting.objects.filter(id=id).first()
    if meeting :
        participations = Participation.objects.filter(meeting=meeting)
        members = []
        for participation in participations :
            members.append(participation.user)
        for user in members :
            user.marker = marker(user.username, color='#660000')
            user.save()
            result = {}
            result['users'] = [user.serialize() for user in members]
            result['loc'] = meeting.location.serialize()
            result['meeting'] = meeting.serialize()
            bubble = f'{meeting.name}\r\n'
            bubble += f'by {meeting.owner.username}\r\n\r\n'
            bubble += f'{meeting.memo}'
            result['bubble'] = bubble
        return JsonResponse(result, safe=False)
    else :
        return JsonResponse(f'group {id} not found', safe=False, status=404)

@login_required
def users_info(request):
    users = User.objects.all()
    for user in users :
        user.marker = marker(user.username, color='#660000')
        user.save()
    return JsonResponse([user.serialize() for user in users], safe=False)

@login_required
def locations_info(request, user_id=0):
    locations = Location.objects.all()
    if user_id > 0 :
        user = User.objects.filter(user_id=user_id).first()
        if user :
            locations = locations.objects.filter(owner=user)
    locs = []
    for location in locations :
        location.marker = marker(location.name)
        location.save()
        ls = location.serialize()
        locs.append(ls)
    return JsonResponse(locs, safe=False)



# __________________________________________________ LOCATION VIEWS ____________

class LocationList(LoginRequiredMixin, ListView) :
    model = Location
    fields = '__all__'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return context

@login_required
def location_delete(request, location_id) :
    location = Location.objects.filter(id=location_id).first()
    if location :
        if (location.owner == request.user) or request.user.is_superuser :
            location.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else'e quote", extra_tags='alert-danger')
    return redirect(reverse('meeting:location_list'))

@login_required
def resize_60x60(request, id) :
    location = Location.objects.filter(id=id).first()
    if location :
        f = location.fullname()
        try :
            image = Image.open(f)
            if image :
                image.thumbnail((60,60))
                image.save(f)
        except :
            messages.info(request, 'resize failed', extra_tags='alert-danger')
        try :
            location.save()
        except :
            messages.info(request, 'WTF?', extra_tags='alert-danger')
        return redirect(reverse('meeting:location_update', args=[location.id]))
    else :
        return redirect(reverse('meeting:location_list'))

@login_required
def update_last_location(request) :
    location = Location.objects.all().last()
    if location :
        return redirect(reverse('meeting:resize_60x60', args=[location.id]))
    else :
        return redirect(reverse('meeting:location_list'))


class LocationUpdate(LoginRequiredMixin, UpdateView) :
    model = Location
    form_class = LocationForm
    template_name = 'meeting/location_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        locations = Location.objects.filter(owner=self.request.user)
        context['object_list'] = locations
        return context

    def form_valid(self, form):
        self.success_url = reverse('meeting:resize_60x60', args=[form.instance.id])
        # messages.info(self.request, f'form is valid {form}  \n\r request {self.request}', extra_tags='alert-success')
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LocationCreate(LoginRequiredMixin, CreateView) :
    model = Location
    form_class = LocationForm
    template_name = 'meeting/location_list.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.success_url = reverse('meeting:update_last_location')
        return super().form_valid(form)

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(LocationCreate, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['owner'] = self.request.user
        return initial

# _____________________________________________ MEETING VIEWS __________________


class MeetingList(LoginRequiredMixin, ListView) :
    model = Meeting

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        meetings = Meeting.objects.all().annotate(Count('members'));

        meeting_list = []

        for meeting in meetings :
            item = {}
            item['meeting'] = meeting
            participations = Participation.objects.filter(meeting=meeting)
            count = participations.count()
            item['count'] = count
            members = []
            for participation in participations :
                members.append(participation.user)
            item['members'] = members
            meeting_list.append(item)
        context['meeting_list'] = meeting_list
        return context


class MeetingDetail(LoginRequiredMixin, DetailView) :
    model = Meeting

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            meeting = Meeting.objects.filter(id=pk).first();

            users=User.objects.order_by('username')

            participations = Participation.objects.filter(meeting=meeting)
            count = participations.count()
            members = []
            for participation in participations :
                members.append(participation.user)
                users = users.exclude(id=participation.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['meeting'] = meeting
            context['users_not_in_meeting'] = users
        return context


class MeetingCreate(LoginRequiredMixin, CreateView) :
    model = Meeting
    form_class = MeetingForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.success_url = reverse('meeting:meeting_list')
        return super().form_valid(form)


class MeetingUpdate(LoginRequiredMixin, UpdateView) :
    model = Meeting
    form_class = MeetingForm
    template_name = 'meeting/meeting_update_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if 'pk' in self.kwargs :
            pk = self.kwargs['pk']
            meeting = Meeting.objects.filter(id=pk).first();

            users=User.objects.order_by('username')

            participations = Participation.objects.filter(meeting=meeting)
            count = participations.count()
            members = []
            for participation in participations :
                members.append(participation.user)
                # users = users.exclude(id=participation.user.id)
            users_count = users.count()
            context['count'] = count
            context['users_count'] = users_count
            context['members'] = members
            context['meeting'] = meeting
            context['users_not_in_meeting'] = users

            groups = Group.objects.all().annotate(Count('members'));
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

    def form_valid(self, form):
        self.success_url = reverse('meeting:meeting_list')
        return super().form_valid(form)


@login_required
def meeting_delete(request, pk) :
    meeting = Meeting.objects.filter(id=pk).first()
    if meeting :
        if ('meeting.owner' == 'request.user') or request.user.is_superuser :
            meeting.delete()
        else :
            messages.info(request, "You are not allowed to delete someone else'e meeting", extra_tags='alert-danger')
    return redirect(reverse('hub:index'))








