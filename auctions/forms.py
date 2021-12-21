from django import forms
from django.forms import ModelForm, Form
from auctions.models import Listing

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = '__all__'
        exclude = ['created_by', 'active', 'close_price']

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-light-gray w3-input w3-margin w3-large'


class CommentFormInline(Form):
    text = forms.CharField()


class BidForm(Form):
    price = forms.IntegerField()

