from django import forms
from account.models import Post

class PostForm(forms.ModelForm):
    hashtags = forms.CharField(required=False)

    class Meta:
        model = Post
        fields = ['content', 'image', 'hashtags']