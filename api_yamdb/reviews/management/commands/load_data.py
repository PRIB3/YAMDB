import csv
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Title, User, Review


class Command(BaseCommand):
    help = 'Загружает данные из csv файлов в базу данных'

    def handle(self, *args, **kwargs):
        self.load_categories()
        self.load_genres()
        self.load_titles()
        self.load_genre_titles()
        self.load_users()
        self.load_reviews()
        self.load_comments()

    def load_categories(self):
        with open('category.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def load_genres(self):
        with open('genre.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )

    def load_titles(self):
        with open('titles.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=row['category']
                )

    def load_users(self):
        with open('users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )

    def load_reviews(self):
        with open('reviews.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Review.objects.create(
                    id=row['id'],
                    title=row['title_id'],
                    text=row['text'],
                    author=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                )

    def load_comments(self):
        with open('comments.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Comment.objects.create(
                    id=row['id'],
                    text=row['text'],
                    author=row['author'],
                    review=row['review_id'],
                    pub_date=row['pub_date']
                )

    def load_genre_title(self):
        with open('genre_title.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title_id = int(row['title_id'])
                genre_id = int(row['genre_id'])
                title = Title.objects.get(id=title_id)
                genre = Genre.objects.get(id=genre_id)
                title.genre.add(genre)