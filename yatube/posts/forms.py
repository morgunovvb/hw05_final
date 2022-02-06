from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image',)
        widgets = {
            'text': forms.Textarea(),
        }
        labels = {
            'group': 'Группа',
            'text': 'Текст'
        }
        help_texts = {
            'text': 'Текст поста', 'group': 'Группа поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(),
        }
        labels = {
            'text': 'Текст'
        }
