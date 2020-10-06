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
        Genre.objects.create(title="test Genre")
        Genre.objects.create(title="test20 Genre1")

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

    def test_add_CRUD_book(self):
        self.client.force_login(self.user1)
        url = reverse("add_new_book")
        response = self.client.post(url, data={
            'text': 'test text for this book',
            'genre': ['1', '2'],
            'title': 'test title'
        })
        self.assertEqual(response.status_code, 302)
        book = Book.objects.all().first()
        self.assertEqual(book.id, 1)
        url = reverse("update_book", args=['1'])
        response = self.client.post(url, data={
            'text': 'test text for this book',
            'genre': ['1'],
            'title': 'test title'
        })
        self.assertEqual(response.status_code, 302)
        book_genre_count = Book.objects.all().first().genre.count()
        self.assertEqual(book_genre_count, 1)
        url = reverse("delete_book", args=['1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        count = Book.objects.all().count()
        self.assertEqual(count, 0)

    def test_comment_like_book_rate(self):
        self.client.force_login(self.user1)
        book = Book.objects.create(title="test title", text="test text", slug="test slug")
        comment = Comment.objects.create(text="test text", book=book, user=self.user1)
        response = self.client.get(reverse('add_rate', args=['1', '5']))
        self.assertEqual(response.status_code, 302)
        book.refresh_from_db()
        self.assertEqual(book.cached_rate, 5)
        response = self.client.get(reverse('add_comment', args=['1']))
        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.cached_likes, 1)


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
        rate = self.driver. \
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h4[@id='book_rate1']")
        self.assertEqual(rate.text, "Rate: 3,00")
        text = self.driver. \
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/i/h5")
        self.assertEqual(text.text, self.book.text)
        title = self.driver. \
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h1")
        self.assertEqual(title.text, self.book.title)
        publish_date = self.driver. \
            find_element_by_xpath("html/body/div[@class='container']/div[@id='booktest_slug']/h2")
        d = self.book.publish_date
        self.assertEqual(datetime.strptime(publish_date.text, "%d %B %Y г."), datetime(d.year, d.month, d.day))
        genre = self.driver. \
            find_element_by_xpath("/html/body/div/div[1]/i[2]")
        self.assertEqual(genre.text, f"Genre: {' '.join([i.title for i in self.book.genre.all()])}")
        authors = self.driver. \
            find_element_by_xpath("/html/body/div/div[1]/i[3]")
        self.assertEqual(authors.text, f"Authors: {' '.join([i.username for i in self.book.author.all()])}")
        # got to the register
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
        # go to the login
        self.driver.get(f"{self.live_server_url}/shop/login/")
        user_name = self.driver.find_element_by_xpath("/html/body/div/form/input[2]")
        password1 = self.driver.find_element_by_xpath("/html/body/div/form/input[3]")
        submit = self.driver.find_element_by_xpath("/html/body/div/form/button")
        user_name.send_keys('bogdanbogdan')
        password1.send_keys("useruser")
        sleep(1)
        submit.submit()
        # go to
        star = self.driver.find_element_by_xpath("/html/body/div/div[1]/span[5]")
        sleep(0.5)
        star.click()
        text = self.driver.find_element_by_xpath("/html/body/div/div[1]/form/textarea")
        text.send_keys("test comment for my book")
        submit = self.driver.find_element_by_xpath("/html/body/div/div[1]/form/button")
        sleep(0.5)
        submit.submit()
        like1 = self.driver.find_element_by_xpath("/html/body/div/div/div[1]/h6[4]")
        like2 = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/h6[4]")
        sleep(0.5)
        like1.click()
        like2.click()
        like1 = self.driver.find_element_by_xpath("/html/body/div/div/div[1]/h6[4]")
        like2 = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/h6[4]")
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
        self.assertEqual(rate.text, "Rate: 3,25")
        self.driver.get(f'{self.live_server_url}/shop/AddNewBook/')
        sleep(1)
        text = self.driver.find_element_by_xpath("/html/body/div/form/textarea")
        sleep(0.5)
        self.driver.find_element_by_xpath("/html/body/div/form/select/option[text()='test_genre']").click()
        title = self.driver.find_element_by_xpath("/html/body/div/form/input[2]")
        text.send_keys("test text test")
        title.send_keys("test title test")
        sleep(0.5)
        self.driver.find_element_by_xpath("/html/body/div/form/button").submit()
        self.driver.get(f'{self.live_server_url}/shop/update_book/2')
        sleep(0.5)
        self.driver.find_element_by_xpath("/html/body/div/form/button").submit()
        self.driver.find_element_by_xpath("/html/body/div/div[2]/button").click()
        sleep(0.5)
        self.driver.find_element_by_xpath("/html/body/div/div/div[2]/button").click()
        sleep(0.5)
        self.driver.get(f'{self.live_server_url}/shop/logout/')
        # go to fall register
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
        # go to fall login
        self.driver.get(f"{self.live_server_url}/shop/login/")
        user_name = self.driver.find_element_by_xpath("/html/body/div/form/input[2]")
        password1 = self.driver.find_element_by_xpath("/html/body/div/form/input[3]")
        submit = self.driver.find_element_by_xpath("/html/body/div/form/button")
        user_name.send_keys('bogdanbogdan1')
        password1.send_keys("useruser1")
        sleep(1)
        submit.submit()
        sleep(1)

# coverage run --source='.' manage.py test .
# coverage report
# coverage html
