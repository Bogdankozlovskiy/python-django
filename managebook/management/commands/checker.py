from django.core.management import BaseCommand
from managebook.models import Book, BookRate
from django.db.models import Case, Count, When, Avg, PositiveIntegerField, Value, Q, F


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_id = 2
        print(user_id)
