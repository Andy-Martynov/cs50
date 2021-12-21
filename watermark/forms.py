from django import forms

class WatermarkUploadForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    watermark = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(WatermarkUploadForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-light-gray w3-input w3-margin w3-large'

