from django.forms import ModelForm, Textarea, NumberInput, TextInput

from album.models import Animation

class AnimationForm(ModelForm):
    class Meta:
        model = Animation
        fields = '__all__'
        exclude = ('user', 'text', )
        widgets = {
            'title' : TextInput(attrs={'placeholder': 'The name of animation ...', 'required': True, }),
            'duration' : NumberInput(attrs={'placeholder': 'The duration of animation in seconds...', }),
            'keyframes' : Textarea(attrs={'placeholder': 'write CSS keyframes rule here ...', 'rows': '8' }),
            'prefix' : TextInput(attrs={'placeholder': 'Additional prorerties ...', }),
        }

    # def __init__(self, *args, **kwargs):
    #     super(AnimationForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'form-control'

