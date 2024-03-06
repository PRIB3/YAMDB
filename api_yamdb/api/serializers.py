from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, Title, Review, Comment, User
from .validators import year_validate


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    name = serializers.CharField(
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ("name", "slug")
        read_only_fields = ("name",)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    name = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = Genre
        fields = ("name", "slug")
        read_only_fields = ("name",)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    rating = serializers.SerializerMethodField()
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = "__all__"

    def validate_year(self, value) -> int:
        """Валидация года."""

        year_validate(value)
        return value

    def to_representation(self, instance):
        """Изменение слагов на объекты жанров и категорий для вывода."""

        represent = super().to_representation(instance)
        represent["genre"] = GenreSerializer(
            instance.genre.all(),
            many=True
        ).data
        represent["category"] = CategorySerializer(instance.category).data
        return represent

    def get_rating(self, obj) -> int:
        """Расчет рейтинга произведения."""
        if Review.objects.filter(title=obj):
            reviews = obj.reviews.all()
            scores = 0
            for review in reviews:
                scores += review.score
            return int(scores / len(reviews))


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = "__all__"
        extra_kwargs = {
            "title": {"required": False,
                      "write_only": True}
        }


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {
            "review": {"required": False,
                       "write_only": True}
        }


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
