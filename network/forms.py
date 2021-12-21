from django.forms import ModelForm, RadioSelect, TextInput, Select, CharField, NumberInput, Textarea

from .models import Post

class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'author' : TextInput(attrs={'hidden': True}),
            'text' : Textarea(attrs={'placeholder': 'write here ...', 'rows': '2' }),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
