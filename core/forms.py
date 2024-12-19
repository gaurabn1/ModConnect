
from django import forms
from .models import *

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text' : forms.Textarea(attrs={'rows':4, 'placeholder' : 'Enter comment here'}),
        }

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("Image is required.")
        return image

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']


