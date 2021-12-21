from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from account.models import User
from mysite import settings

import json

#____________________________________________________________ PUSHER ___________
import pusher
from pusher_push_notifications import PushNotifications

beams_client = PushNotifications(
    instance_id=settings.BEAM_INSTANCE_ID,
    secret_key=settings.BEAM_SECRET_KEY,
)

pusher_client = pusher.Pusher(
  app_id=settings.PUSHER_APP_ID,
  key=settings.PUSHER_KEY,
  secret=settings.PUSHER_SECRET,
  cluster='eu',
  ssl=True
)

@csrf_exempt
def pusher_auth(request):
    # if not request.user.is_authenticated:
    #     return HttpResponseForbidden()
    image_url = None
    if request.user.image:
        if request.user.image.url:
            image_url = request.user.image.url
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': request.user.id,
            'user_info': {  # We can put whatever we want here
                'username': request.user.username,
                'image': image_url,
            }
        })
    return JsonResponse(payload)

@csrf_exempt
def pusher_beams_auth(request, user_id=None):
    # if not request.user.is_authenticated:
    #     return HttpResponse('User is not authenticated', 403)

    # if user_id != request.user.id:
    #     return HttpResponse('Inconsistent request', 401)

    beams_token = beams_client.generate_token(str(user_id))
    return JsonResponse(beams_token) # {'token': beams_token})


@login_required
def hello(request, text):
    data = {}
    data['username'] = request.user.username
    data['user_id'] = request.user.id
    data['message'] = f'{request.user.username}: {text}'
    pusher_client.trigger('my-channel', 'message-to-all', data)
    return JsonResponse({'message': f'notifiation from {request.user.username} sent'})

@login_required
def beam_hello(request, text):
    response = beams_client.publish_to_interests(
      interests=['hello'],
      publish_body={
        'web': {
          'notification': {
            'title': f'From {request.user.username}',
            'body': text,
            'deep_link': 'https://cs50.pythonanywhere.com',
          },
        },
      },
    )
    return JsonResponse({'message': f'notifiation from {request.user.username} sent'})

@login_required
def beam_user_message(request, id):
    beams_client = PushNotifications(
        instance_id='4db9511e-c5da-4d6f-8f58-9fbee669a07f',
        secret_key='1084B2BACEE2B3988B64C932B6842735CEB36BC1DAFB7A493FA130E604169778',
    )
    user=User.objects.filter(id=id).first()
    if user:
        user_ids = []
        user_ids.append(str(id))
        response = beams_client.publish_to_users(
            user_ids=user_ids,
            publish_body={
            'web': {
              'notification': {
                'title': 'Message',
                'body': f'{user.username}, you have a message from {request.user.username}',
                'deep_link': 'https://cs50.pythonanywhere.com',
              },
            },
          },
        )
    return JsonResponse({'message': f'message from {request.user.username} sent to {user.username}, {response}'})

def index(request):
    context = {}
    context['events'] = ['test', 'four_game_canceled', 'four_game_started', 'four_message']
    return render(request, 'rtc/index.html', context)

@csrf_exempt
def test(request):
    if request.method == 'POST' : # options changed
        post = json.loads(request.body)
        if 'event' in post :
            event = post['event']
            data = {}
            message = 'event ' + event + ' triggered!'
            data['message'] = message
            pusher_client.trigger('my-channel', event, data)
            return JsonResponse({'message':message, 'status':200})
        return JsonResponse({'message':'No event', 'status':400})
    return JsonResponse({'message':'Bad method', 'status':400})

@csrf_exempt
def trigger(request):
    if request.method == 'POST' : # options changed
        data = {}
        data['kind'] = 'tic-tac-toe'
        data['game_id'] = 100
        message = 'event game_cancelled triggered!'
        data['message'] = message
        pusher_client.trigger('my-channel', 'game_canceled', data)
        return JsonResponse({'message':message, 'status':200})













