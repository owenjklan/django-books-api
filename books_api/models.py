from django.db import models


class BookFormatChoices(models.TextChoices):
    HARDBACK = "Hard Cover"
    PAPERBACK = "Paperback"
    EBOOK = "Ebook"


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    format = models.CharField(max_length=25, choices=BookFormatChoices.choices)
    rrp = models.DecimalField(max_digits=5, decimal_places=2)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    year_of_birth = models.PositiveSmallIntegerField()
    year_of_death = models.PositiveSmallIntegerField(null=True, blank=True)
    books = models.ManyToManyField("Book", related_name="authors")


class Publisher(models.Model):
    name = models.CharField(max_length=255)


class Category(models.Model):
    name = models.CharField(max_length=255)
    books = models.ManyToManyField("Book", related_name="categories")
