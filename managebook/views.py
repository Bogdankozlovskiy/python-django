from django.shortcuts import render, redirect
from managebook.models import Book, BookRate, CommentLike
from django.views.generic import View
from django.db.models import F, CharField, Value, Q
from django.db.models.functions import Cast


class HelloView(View):
    def get(self, request):
        if request.user.id:
            q = Q(book_like__user_id=request.user.id)
            sub_query = Book.objects.filter(~q).annotate(user_rate=Value(0, CharField()))
            query = Book.objects.filter(q) \
                .annotate(user_rate=Cast("book_like__rate", CharField())) \
                .prefetch_related('genre', 'author', 'comment__user') \
                .union(sub_query).all()
        else:
            query = Book.objects.prefetch_related('genre', 'author', 'comment__user').all()
        return render(request, "index.html", {"content": query})


class AddComment(View):
    def get(self, request, id):
        CommentLike.objects.create(user_id=request.user.id, comment_id=id)
        return redirect("hello")


class AddRate(View):
    def get(self, request, id, rate):
        BookRate.objects.create(user_id=request.user.id, book_id=id, rate=rate)
        return redirect("hello")
