from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class Genre(models.Model):
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    title = models.CharField(max_length=50, verbose_name="название")

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
    slug = models.SlugField(unique=True, verbose_name="Слаг")
    text = models.TextField(verbose_name="текст")
    author = models.ManyToManyField(User, verbose_name="автор", db_index=True)
    publish_date = models.DateField(auto_now_add=True)
    genre = models.ManyToManyField("managebook.Genre", verbose_name="жанр")
    rate = models.ManyToManyField(User, through="managebook.BookRate", related_name="user")
    cached_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name="текст")
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь", related_name="comment")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Книга", related_name="comment")
    like = models.ManyToManyField(User, through='managebook.CommentLike', related_name="liked_comment")
    cached_likes = models.PositiveIntegerField(default=0)


class BookRate(models.Model):
    class Meta:
        unique_together = ("user", 'book')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_like")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_like")
    rate = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.book.cached_rate = self.book.book_like.aggregate(avg_rate=Avg("rate"))['avg_rate']
        self.book.save()


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.comment.cached_likes += 1
        self.comment.save()
