from django.forms import ModelForm, Textarea, NumberInput, TextInput

from folders.models import Folder
from .models import Link

class LinksFolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = ('name', )
        widgets = {
            'name' : TextInput(attrs={'placeholder': 'folder name'}),
        }

    def __init__(self, *args, **kwargs):
        super(LinksFolderForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-input w3-round-xlarge w3-light-gray p-1 my-1 mx-0'

class LinkForm(ModelForm):
    class Meta:
        model = Link
        fields = ('url', 'name', 'tags')
        widgets = {
            'url' : TextInput(attrs={'placeholder': 'URL'}),
            'name' : TextInput(attrs={'placeholder': 'name'}),
            'tags' : TextInput(attrs={'placeholder': 'tags'}),
        }

    def __init__(self, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-input w3-round-xlarge w3-light-gray p-1 my-1 mx-0'

