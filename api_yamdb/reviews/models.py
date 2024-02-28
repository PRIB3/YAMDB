from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

from .utils import ROLES, SCORES


class Profile(AbstractUser):
    """
    Модель для пользователей.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Обязательное поле. 150 символов или меньше. Допустимы буквы, цифры и символы @/./+/-/_."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _(
                "Пользователь с таким именем пользователя уже существует."
            ),
            "max_length": _(
                "Длина имени пользователя не должна превышать 150 символов."
            ),
        },
    )
    role = models.CharField(choices=ROLES, default="user", max_length=150)
    bio = models.TextField(null=True, blank=True)
    email = models.EmailField(_("email address"), max_length=254)


User = get_user_model()


class Genre(models.Model):
    """
    Модель для жанров.
    """

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)


class Category(models.Model):
    """
    Модель для категорий.
    """

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50)


class Title(models.Model):
    """
    Модель для произведений.
    """

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="titles", null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
    )


class Review(models.Model):
    """
    Модель для отзывов.
    """

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    score = models.IntegerField(choices=SCORES)
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    """
    Модель для комментариев.
    """

    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    pub_date = models.DateTimeField(auto_now_add=True)
