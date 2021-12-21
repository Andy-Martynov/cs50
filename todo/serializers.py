from rest_framework import serializers

from .models import Task
from account.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['title']

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

# RecursiveField(many=True)

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        lookup_field = 'pk'

    # user = UserSerializer(read_only=True)
    # parent = serializers.PrimaryKeyRelatedField(read_only=True)
    # name = serializers.CharField(max_length=200)
    # text = serializers.CharField(max_length=1000)
    # level = serializers.IntegerField()
    # subtasks = RecursiveField(many=True, read_only=True)


