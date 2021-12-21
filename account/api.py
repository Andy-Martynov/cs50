from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required

import json

from .models import User, Group, Membership


@login_required
def user_info(request, id):
    user = User.objects.filter(id=id).first()
    if user :
        my_groups = []
        for group in Group.objects.filter(creator=user):
            my_groups.append(group.serialize())

        memberships = Membership.objects.filter(user=user)
        groups_im_in = []
        for membership in memberships:
            if not membership.group.creator == user:
                groups_im_in.append(membership.group.serialize())
        image_url = None
        if request.user.image:
            if request.user.image.url:
                image_url = request.user.image.url
        info={
            'user_id': request.user.id,
            'username': request.user.username.replace('_', ' '),
            'image': image_url,
            'my_groups': my_groups,
            'groups_im_in': groups_im_in,
            }
        return JsonResponse(info, status=200)
    return JsonResponse({'error': f'user {id} not found'}, status=404)

@login_required
def group_info(request, id):
    group = Group.objects.filter(id=id).first()
    if group :
        memberships = Membership.objects.filter(group=group)
        members = []
        for membership in memberships:
            # if membership.user != request.user:
            members.append(membership.user.serialize())
        info={
            'group_id': group.id,
            'groupname': group.name,
            'creator': group.creator.username.replace('_', ' '),
            'members': members,
            }
        return JsonResponse(info, status=200)
    return JsonResponse({'error': f'user {id} not found'}, status=404)


