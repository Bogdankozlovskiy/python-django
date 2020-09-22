from django.forms import BaseForm, Form, ModelForm, CharField, Textarea, TextInput, SelectMultiple, SlugField
from managebook.models import Comment, Book
from django.contrib import messages


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'rows': 5})
        }
        labels = {'text': 'do you want to live a comment?'}


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("text", "genre", "title")
        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'title': TextInput(attrs={'class': 'form-control'}),
            'genre': SelectMultiple(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'title': '',
        }
