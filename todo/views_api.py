from django.shortcuts import render

from account.models import User
from .models import Task

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.contrib.auth import login

from .serializers import TaskSerializer

class TaskViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving tasks.
    """
    lookup_field = 'pk'

    def list(self, request):
        queryset = Task.objects.all()
        serializer = TaskSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Task.objects.all()
        task = get_object_or_404(queryset, pk=pk)
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)

# class TaskList(generics.ListAPIView):
#     """
#     ### Get task list

#     """
#     serializer_class = TaskSerializer
#     # permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         if not 'user_id' in self.kwargs:
#             return Task.objects.all()

#         user_id = self.kwargs['user_id']

#         user = User.objects.filter(id=user_id).first()
#         if not user:
#             return Response({"error": f"User {user_id} not found"})
#         else:
#             tasks = Task.objects.filter(user=user)
#         queryset = tasks
#         return queryset


# class TaskDetail(APIView):
#     """
#     ### Get task
#     """
#     # serializer_class = TaskSerializer
#     # permission_classes = [permissions.IsAuthenticated]

#     def get(self, request,  pk=None):
#         # if not 'pk' in self.kwargs:
#         #     return Response({"error": "No <pk> in kwargs"})

#         # pk = int(self.kwargs['pk'])

#         task = Task.objects.filter(pk=pk).first()

#         answer = {}
#         answer['pk'] = task.pk
#         answer['user'] = task.user
#         answer['parent'] = task.parent
#         answer['name'] = task.name
#         answer['text'] = task.text
#         answer['level'] = task.level
#         answer['subtasks'] = task.subtasks

#         serializer = TaskSerializer(data=answer, context={'request': request})
#         if serializer.is_valid():
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors)

def index(request):
    return render(request, "todo/index.html")


