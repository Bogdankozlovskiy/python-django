from datetime import datetime
from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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


class TestInterface(StaticLiveServerTestCase):
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
        self.comment = Comment.objects.create(text="test text", book=self.book, user=self.user1)
        CommentLike.objects.create(comment=self.comment, user=self.user1)
        CommentLike.objects.create(comment=self.comment, user=self.user2)
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
        genre = self.driver.\
            find_element_by_xpath("/html/body/div/div[1]/i[2]")
        self.assertEqual(genre.text, f"Genre: {' '.join([i.title for i in self.book.genre.all()])}")
        authors = self.driver.\
            find_element_by_xpath("/html/body/div/div[1]/i[3]")
        self.assertEqual(authors.text, f"Authors: {' '.join([i.username for i in self.book.author.all()])}")
        self.driver.get(f"{self.live_server_url}/shop/register/")
        user_name = self.driver.find_element_by_xpath("/html/body/div/form/input[2]")
        password1 = self.driver.find_element_by_xpath("/html/body/div/form/input[3]")
        password2 = self.driver.find_element_by_xpath("/html/body/div/form/input[4]")
        submit = self.driver.find_element_by_xpath("/html/body/div/form/button")
        user_name.send_keys('bogdanbogdan')
        password1.send_keys("useruser")
        password2.send_keys("useruser")
        sleep(1)
        submit.submit()
        self.driver.get(f"{self.live_server_url}/shop/login/")
        user_name = self.driver.find_element_by_xpath("/html/body/div/form/input[2]")
        password1 = self.driver.find_element_by_xpath("/html/body/div/form/input[3]")
        submit = self.driver.find_element_by_xpath("/html/body/div/form/button")
        user_name.send_keys('bogdanbogdan')
        password1.send_keys("useruser")
        sleep(1)
        submit.submit()
        star = self.driver.find_element_by_xpath("/html/body/div/div[1]/span[5]")
        sleep(0.5)
        star.click()
        text = self.driver.find_element_by_xpath("/html/body/div/div[1]/form/textarea")
        text.send_keys("test comment for my book")
        submit = self.driver.find_element_by_xpath("/html/body/div/div[1]/form/button")
        sleep(0.5)
        submit.submit()
        like1 = self.driver.find_element_by_xpath("/html/body/div/div[1]/h6[4]")
        like2 = self.driver.find_element_by_xpath("/html/body/div/div[1]/h6[8]")
        sleep(0.5)
        like1.click()
        like2.click()
        like1 = self.driver.find_element_by_xpath("/html/body/div/div[1]/h6[4]")
        like2 = self.driver.find_element_by_xpath("/html/body/div/div[1]/h6[8]")
        self.comment.refresh_from_db()
        self.assertEqual(like1.text, f"Likes: {self.comment.cached_likes}")
        cl_before = like2.get_attribute("class")
        self.assertEqual(cl_before, like1.get_attribute("class"))
        like2.click()
        sleep(0.5)
        cl_after = like2.get_attribute("class")
        self.assertNotEqual(cl_after, cl_before)
        star_4 = self.driver.find_element_by_xpath("/html/body/div/div[1]/span[4]")
        star_4.click()
        star_5 = self.driver.find_element_by_xpath("/html/body/div/div[1]/span[5]")
        sleep(0.5)
        self.assertNotEqual(star_4.get_attribute("class"), star_5.get_attribute("class"))
        rate = self.driver. \
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h4[@id='book_rate1']")
        self.assertEqual(rate.text, "Rate: 3.25")




