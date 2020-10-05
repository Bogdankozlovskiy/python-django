from datetime import datetime
from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models import Avg


class Genre(models.Model):
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    title: str = models.CharField(max_length=50, verbose_name="название")

    def __str__(self):
        return self.title


class Book(models.Model):
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    title = models.CharField(
        max_length=50,
        verbose_name="название",
        help_text="help text",
        db_index=True
    )
    slug: str = models.SlugField(unique=True, verbose_name="Слаг")
    text: str = models.TextField(verbose_name="текст")
    author: User = models.ManyToManyField(User, verbose_name="автор", db_index=True, related_name="book")
    publish_date: datetime = models.DateField(auto_now_add=True, verbose_name="дата публикации")
    genre = models.ManyToManyField("managebook.Genre", verbose_name="жанр")
    rate = models.ManyToManyField(User, through="managebook.BookRate", related_name="user")
    cached_rate: float = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="рэйтинг")

    def __str__(self):
        return self.title


class Comment(models.Model):
    text: str = models.TextField(verbose_name="текст")
    date: datetime = models.DateTimeField(auto_now_add=True)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь", related_name="comment")
    book: Book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга", related_name="comment")
    like = models.ManyToManyField(User, through='managebook.CommentLike', related_name="liked_comment")
    cached_likes: int = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.text[:25] + "..."


class BookRate(models.Model):
    class Meta:
        unique_together = ("user", 'book')

    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_like")
    book: Book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_like")
    rate: int = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            br = BookRate.objects.get(user=self.user, book=self.book)
            br.rate = self.rate
            return br.save()
        else:
            self.book.cached_rate = self.book.book_like.aggregate(avg_rate=Avg("rate"))['avg_rate']
            self.book.save()
            return self.book.cached_rate


class CommentLike(models.Model):
    class Meta:
        unique_together = ("user", 'comment')

    comment: Comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            CommentLike.objects.get(user=self.user, comment=self.comment).delete()
            self.comment.cached_likes -= 1
            self.comment.save()
            return False, self.comment.cached_likes
        else:
            self.comment.cached_likes += 1
            self.comment.save()
            return True, self.comment.cached_likes
