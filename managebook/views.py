from django.shortcuts import render, redirect
from pytils.translit import slugify
from managebook.forms import CommentForm, BookForm
from managebook.models import Book, BookRate, CommentLike
from django.views.generic import View
from django.db.models import F, CharField, Value, Q, Case, When
from django.db.models.functions import Cast
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages


class HelloView(View):
    def get(self, request):
        if request.user.is_authenticated:
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
        return render(request, "index.html", {"content": query.order_by('-publish_date'), "comment_form": CommentForm()})


class AddCommentLike(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            CommentLike.objects.create(user_id=request.user.id, comment_id=id)
        return redirect("hello")


class AddRate(View):
    def get(self, request, id, rate):
        if request.user.is_authenticated:
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


class AddComment(View):
    def post(self, request, id):
        comment = CommentForm(renderer=request, data=request.POST)
        if comment.is_valid():
            new_comment = comment.save(commit=False)
            new_comment.book_id = id
            new_comment.user_id = request.user.id
            new_comment.save()
            comment.save_m2m()
        return redirect('hello')


class AddNewBook(View):
    def get(self, request):
        bf = BookForm()
        return render(request, "add_new_book.html", {'book_form': bf, 'id': 0})

    def post(self, request):
        bf = BookForm(renderer=request, data=request.POST)
        if bf.is_valid():
            new_book = bf.save(commit=False)
            new_book.slug = slugify(bf.cleaned_data['title'])
            new_book.save()
            new_book.author.add(request.user)
            bf.save_m2m()
        return redirect('hello')


class UpdateBook(View):
    def get(self, request, id):
        book = Book.objects.get(id=id)
        bf = BookForm(instance=book)
        return render(request, 'update_book.html', {'book_form': bf, "id": book.id})

    def post(self, request, id):
        book = Book.objects.get(id=id)
        f = BookForm(request.POST, instance=book)
        f.save()
        return redirect('hello')


class DeleteBook(View):
    def get(self, request, id):
        Book.objects.get(id=id).delete()
        return redirect('hello')
