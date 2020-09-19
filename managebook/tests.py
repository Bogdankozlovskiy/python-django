from django.test import TestCase
from managebook.models import Book, BookRate, Comment, CommentLike
from django.contrib.auth.models import User
from django.db.models import Avg


class TestRateBook(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test1")
        self.user2 = User.objects.create(username='Test2')
        self.user3 = User.objects.create(username="Test3")

    def test_rate(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        BookRate.objects.create(user=self.user1, book=book, rate=3)
        BookRate.objects.create(user=self.user2, book=book, rate=4)
        BookRate.objects.create(user=self.user3, book=book, rate=2)
        rate = book.book_like.aggregate(avg_rate=Avg("rate"))
        self.assertEqual(rate['avg_rate'], 3)

    def test_cached_rate(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        BookRate.objects.create(user=self.user1, book=book, rate=3)
        BookRate.objects.create(user=self.user2, book=book, rate=4)
        BookRate.objects.create(user=self.user3, book=book, rate=2)
        self.assertEqual(book.cached_rate, 3)

    def test_like(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        comment = Comment.objects.create(text="test text", book=book, user=self.user1)
        comment.like.add(self.user2)
        comment.like.add(self.user3)
        likes = comment.like.all().count()
        self.assertEqual(likes, 2)

    def test_cached_likes(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        comment = Comment.objects.create(text="test text", book=book, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user2)
        self.assertEqual(comment.cached_likes, 2)
# Create your tests here.
