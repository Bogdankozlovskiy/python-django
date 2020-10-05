from datetime import datetime
from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from managebook.models import Book, BookRate, Comment, CommentLike, Genre
from django.contrib.auth.models import User
from django.db.models import Avg
from selenium.webdriver import Chrome


class TestRateBook(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="Test1")
        self.user2 = User.objects.create(username='Test2')
        self.user3 = User.objects.create(username="Test3")

    def test_rate(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        BookRate.objects.bulk_create([
            BookRate(user=self.user1, book=book, rate=3),
            BookRate(user=self.user2, book=book, rate=4),
            BookRate(user=self.user3, book=book, rate=2)
        ])
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
        CommentLike.objects.bulk_create([
            CommentLike(user=self.user1, comment=comment),
            CommentLike(user=self.user2, comment=comment),
        ])
        likes = comment.like.all().count()
        self.assertEqual(likes, 2)

    def test_cached_likes(self):
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        comment = Comment.objects.create(text="test text", book=book, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user2)
        self.assertEqual(comment.cached_likes, 2)


class TestInterface(LiveServerTestCase):
    def setUp(self):
        self.gnre = Genre.objects.create(title="test_genre")
        self.user1 = User.objects.create(username="Test1", password='1234')
        self.user2 = User.objects.create(username='Test2', password='1234')
        self.user3 = User.objects.create(username="Test3", password='1234')
        self.book = Book.objects.create(title="test title", text="test text", slug="test_slug")
        self.book.genre.add(self.gnre)
        self.book.author.add(self.user1)
        self.book.author.add(self.user2)
        self.book.save()
        BookRate.objects.create(user=self.user1, book=self.book, rate=3)
        BookRate.objects.create(user=self.user2, book=self.book, rate=4)
        BookRate.objects.create(user=self.user3, book=self.book, rate=2)
        comment = Comment.objects.create(text="test text", book=self.book, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user1)
        CommentLike.objects.create(comment=comment, user=self.user2)
        self.driver = Chrome()
        self.url = reverse("hello")

    def test_ajax_rate(self):
        self.driver.get(f"{self.live_server_url}{self.url}")
        rate = self.driver.\
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h4[@id='book_rate1']")
        self.assertEqual(rate.text, "Rate: 3,00")
        text = self.driver.\
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/i/h5")
        self.assertEqual(text.text, self.book.text)
        title = self.driver.\
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h1")
        self.assertEqual(title.text, self.book.title)
        publish_date = self.driver.\
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h2")
        d = self.book.publish_date
        self.assertEqual(datetime.strptime(publish_date.text, "%d %B %Y г."), datetime(d.year, d.month, d.day))

# Create your tests here.
