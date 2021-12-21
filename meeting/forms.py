from django.forms import ModelForm, Textarea

from .models import Location, Meeting

class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = '__all__'
        exclude = ('owner', )
        widgets = {
            'memo' : Textarea(attrs={'placeholder': 'write event info here ...', 'rows': '3' }),
        }

    def __init__(self, *args, **kwargs):
        super(MeetingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

