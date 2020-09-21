from django.shortcuts import render, redirect
from managebook.models import Book, BookRate, CommentLike
from django.views.generic import View
from django.db.models import F, CharField, Value, Q, Case, When
from django.db.models.functions import Cast
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages


class HelloView(View):
    def get(self, request):
        if request.user.id:
            q = Q(book_like__user_id=request.user.id)
            sub_query = Book.objects.filter(~q) \
                .annotate(user_rate=Value(0, CharField())) \
                .prefetch_related('genre', 'author', 'comment__user')
            query = Book.objects.filter(q) \
                .annotate(user_rate=Cast("book_like__rate", CharField())) \
                .prefetch_related('genre', 'author', 'comment__user') \
                .union(sub_query)
        else:
            query = Book.objects.prefetch_related('genre', 'author', 'comment__user')
        return render(request, "index.html", {"content": query})


class AddComment(View):
    def get(self, request, id):
        if request.user.id:
            CommentLike.objects.create(user_id=request.user.id, comment_id=id)
        return redirect("hello")


class AddRate(View):
    def get(self, request, id, rate):
        if request.user.id:
            BookRate.objects.create(user_id=request.user.id, book_id=id, rate=rate)
        return redirect("hello")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('hello')


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
        else:
            messages.error(request, "password or login is uncorrected")
            return redirect('login')
        return redirect('hello')


class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "this login already exists")
            return redirect('register')
        return redirect('hello')
