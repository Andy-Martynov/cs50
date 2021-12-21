from django import forms
from django.forms import ModelForm, Form, RadioSelect, TextInput, Select, SelectMultiple, CharField, NumberInput, Textarea, ChoiceField

user_images = 'account/images/'

from .models import User, Group

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email',]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UserImageForm(ModelForm):
    class Meta:
        model = User
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(UserImageForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        exclude = ('creator', )
        widgets = {
            'members' : SelectMultiple(attrs={'size': '15'}),
        }

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class PasswordResetEmailForm(Form):

    email = forms.EmailField(label='e-mail')

    def __init__(self, *args, **kwargs):
        super(PasswordResetEmailForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-light-gray w3-input w3-margin w3-large'



