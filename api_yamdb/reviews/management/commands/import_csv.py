"""Команда для импорта csv-файлов."""
import csv

from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Comment, Genre,
    Review, Title, User
)


csv_files = [
    'category.csv',
    'genre.csv',
    'titles.csv',
    'genre_title.csv',
    'users.csv',
    'review.csv',
    'comments.csv'
]

csv_fields = {
    'category.csv': ['id', 'name', 'slug'],
    'comments.csv': ['id', 'review_id', 'text', 'author', 'pub_date'],
    'genre.csv': ['id', 'name', 'slug'],
    'genre_title.csv': ['id', 'title_id', 'genre_id'],
    'review.csv': ['id', 'title_id', 'text', 'author', 'score', 'pub_date'],
    'titles.csv': ['id', 'name', 'year', 'category'],
    'users.csv': [
        'id', 'username', 'email', 'role', 'bio', 'first_name', 'last_name'
    ],
}

Models = {
    'category': Category,
    'comments': Comment,
    'genre': Genre,
    'genre_title': Title.genre.through,
    'review': Review,
    'titles': Title,
    'users': User,
}


def csv_reader_file(csv_file_name):
    """Функция чтения из файла."""
    with open(
        'static/data/' + csv_file_name,
        'r',
        encoding='utf-8'
    )as csvfile:
        csvreader = csv.DictReader(csvfile)
        return list(csvreader)


class Command(BaseCommand):
    """Класс команды."""

    def handle(self, *args, **options):
        """Функция валидации полей и импорта."""
        for csv_file_name in csv_files:
            for row in csv_reader_file(csv_file_name):
                model = csv_file_name.split('.')[0]
                model_class = Models.get(model)
                item = None
                if model_class == User:
                    item = User(
                        id=int(row['id']),
                        username=row['username'],
                        email=row['email'],
                        role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        password='qwerty12345'
                    )
                elif model_class == Category:
                    item = Category(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug']
                    )
                elif model_class == Review:
                    title_id = int(row['title_id'])
                    author_id = int(row['author'])
                    item = Review(
                        id=int(row['id']),
                        title=Title.objects.get(pk=title_id),
                        text=row['text'],
                        author=User.objects.get(pk=author_id),
                        score=int(row['score']),
                        pub_date=row['pub_date']
                    )
                elif model_class == Comment:
                    review_id = int(row['review_id'])
                    author_id = int(row['author'])
                    item = Comment(
                        id=int(row['id']),
                        review=Review.objects.get(pk=review_id),
                        text=row['text'],
                        author=User.objects.get(pk=author_id),
                        pub_date=row['pub_date']
                    )
                elif model_class == Genre:
                    item = Genre(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug']
                    )
                elif model_class == Title:
                    category_id = int(row['category'])
                    item = Title(
                        name=row['name'],
                        year=int(row['year']),
                        category=Category.objects.get(pk=category_id)
                    )
                elif model_class == Title.genre.through:
                    genre_id = int(row['genre_id'])
                    title_id = int(row['title_id'])
                    item = Title.genre.through.objects.create(
                        genre=Genre.objects.get(pk=genre_id),
                        title=Title.objects.get(pk=title_id)
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Не удалось создать запись {model}'
                        )
                    )
                    continue
                item.full_clean()
                item.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Запись для модели {model} добавлена: {row}'
                    )
                )
