from django.shortcuts import render, redirect
from pytils.translit import slugify
from managebook.forms import CommentForm, BookForm, CustomUserCreationForm, CustomAuthenticationForm
from managebook.models import Book, BookRate, CommentLike, Comment
from django.views.generic import View
from django.db.models import CharField, OuterRef, Exists, Prefetch
from django.db.models.functions import Cast
from django.contrib.auth import logout, login
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.models import Subquery
from django.http.response import JsonResponse


class HelloView(View):
    @method_decorator(cache_page(5))
    def get(self, request):
        if request.user.is_authenticated:
            subquery_1 = BookRate.objects.filter(book=OuterRef("pk"), user=request.user).values("rate")
            subquery_2 = CommentLike.objects.filter(comment=OuterRef("pk"), user=request.user)
            queryset = Comment.objects.annotate(isliked=Exists(subquery_2)).select_related('user')
            prefetch = Prefetch("comment", queryset=queryset)
            content = Book.objects.annotate(user_rate=Cast(Subquery(subquery_1), CharField())). \
                prefetch_related('genre', 'author', prefetch)
        else:
            content = Book.objects.prefetch_related('genre', 'author', 'comment__user')
        content = content.order_by('-publish_date')
        return render(request, "index.html", {"content": content, "comment_form": CommentForm()})


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
        form = CustomAuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
        else:
            messages.error(request, "password or login is uncorrected")
            return redirect('login')
        return redirect('hello')


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hello')
        messages.error(request, "this login already exists")
        return redirect('register')


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


class AddAjaxLike(View):
    def post(self, request):
        cl = CommentLike(user=request.user, comment_id=request.POST["comment_id"])
        result = cl.save()
        return JsonResponse({'flag': result[0], "likes": result[1]})


class AddAjaxRate(View):
    def post(self, request):
        data = request.POST['rate_id'].split('/')
        br = BookRate(user=request.user, book_id=data[0], rate=data[1])
        cached_rate = br.save()
        return JsonResponse({"rate": cached_rate, "stars": data[1]})
