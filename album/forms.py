from django.forms import ModelForm, Textarea, NumberInput

from .models import Item, Album, Extention

# class AnimationForm(ModelForm):
#     class Meta:
#         model = Animation
#         fields = '__all__'
#         widgets = {
#             'text' : Textarea(attrs={'placeholder': 'write CSS rule here ...', 'rows': '5' }),
#             'keyframes' : Textarea(attrs={'placeholder': 'write CSS keyframes rule here ...', 'rows': '10' }),
#         }

#     def __init__(self, *args, **kwargs):
#         super(AnimationForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'


class ExtentionForm(ModelForm):
    class Meta:
        model = Extention
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ExtentionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'text', 'file', 'animation')
        widgets = {
            'text' : Textarea(attrs={'placeholder': 'write info here ...', 'rows': '10' }),
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class YouTubeForm(ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'text', 'youtube', )
        widgets = {
            'text' : Textarea(attrs={'placeholder': 'write info here ...', 'rows': '3' }),
        }

    def __init__(self, *args, **kwargs):
        super(YouTubeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


# class LinkForm(ModelForm):
#     class Meta:
#         model = Item
#         fields = ('link', 'title', )
#         widgets = {
#             'title' : Textarea(attrs={'placeholder': 'write title here ...', 'rows': '5' }),
#         }

#     def __init__(self, *args, **kwargs):
#         super(LinkForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = ('title', 'text', 'thumb', 'music', 'def_thumb_width', 'def_thumb_height', 'max_image_width', 'max_image_height', 'animation', 'watermark', 'interval', 'opacity')
        widgets = {
            'text' : Textarea(attrs={'placeholder': 'write info here ...', 'rows': '2' }),
            'opacity' : NumberInput(attrs={'min': '0', 'max': '1', 'step': '0.1', 'value': '0.5' }),
        }

    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

# class LinkFolderForm(ModelForm):
#     class Meta:
#         model = Album
#         fields = ('title',)

#     def __init__(self, *args, **kwargs):
#         super(LinkFolderForm, self).__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             visible.field.widget.attrs['class'] = 'form-control'

