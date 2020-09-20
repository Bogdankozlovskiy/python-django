from django.shortcuts import render, redirect
from managebook.models import Book, BookRate, CommentLike
from django.views.generic import View


class HelloView(View):
    def get(self, request):
        response = {"content": Book.objects.prefetch_related('genre', 'author', 'comment__user').all()}
        return render(request, "index.html", response)


class AddComment(View):
    def get(self, request, id):
        CommentLike.objects.create(user_id=request.user.id, comment_id=id)
        return redirect("hello")


class AddRate(View):
    def get(self, request, id, rate):
        BookRate.objects.create(user_id=request.user.id, book_id=id, rate=rate)
        return redirect("hello")
