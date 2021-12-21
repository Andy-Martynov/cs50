from django.forms import ModelForm, Textarea, NumberInput, TextInput

from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ('user', 'level', 'parent', 'prev', 'next')
        widgets = {
            'name' : TextInput(attrs={'placeholder': 'write task name ...'}),
            'text' : Textarea(attrs={'placeholder': 'write task details ...', 'rows': '3' }),
            'todo' : Textarea(attrs={'placeholder': 'write todo list ...', 'rows': '10' }),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-input w3-round-xlarge w3-light-gray p-1 my-1 mx-0'

