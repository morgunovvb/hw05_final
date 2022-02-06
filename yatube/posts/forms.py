from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post, User


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
