from django.contrib.auth import password_validation
from django.forms import ModelForm, CharField, Textarea, TextInput, SelectMultiple, PasswordInput
from managebook.models import Comment, Book
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=TextInput(attrs={'autofocus': True, "class": "form-control"}))
    password = CharField(
        label="Password",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password', "class": "form-control"}),
    )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        widgets = {
            'username': TextInput(attrs={"class": "form-control"}),
        }

    password1 = CharField(
        label="Password",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = CharField(
        label="Password confirmation",
        widget=PasswordInput(attrs={'autocomplete': 'new-password', "class": "form-control"}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )


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
