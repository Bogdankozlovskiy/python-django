from django.core.management import BaseCommand
from managebook.models import Book
from django.db.models import Case, Count, When, Avg, PositiveIntegerField, Value, Q, F, CharField
from django.db.models.functions import Cast


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_id = 3
        q = Q(book_like__user_id=user_id)
        sub_query = Book.objects.filter(~q).annotate(user_rate=Value(0, CharField()))
        query = Book.objects.filter(q) \
            .annotate(user_rate=Cast("book_like__rate", CharField())) \
            .union(sub_query).all()
        if query:
            print(vars(query[0]))
        else:
            print(query)
