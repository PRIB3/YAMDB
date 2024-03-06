from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.db.models.query import QuerySet

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from reviews.models import Category, Genre, Title, Review, Comment, User
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
)
from .permissions import (IsUserAdminOrReadOnly,
                          IsUserAuthenticated,
                          IsUserOwnerOrStaff,
                          IsUserAdmin)


@api_view(["POST"])
def signup(request) -> Response:
    """Обработчик регистрации"""

    if request.data["username"] == "me":
        raise serializers.ValidationError('Имя "me" нельзя использовать')

    if User.objects.filter(
        username=request.data["username"],
        email=request.data["email"]
        ):
        user = User.objects.get(username=request.data["username"], email=request.data["email"])
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="Confirmation Code from Ya.MDB",
            message=f"Confirmation code: {confirmation_code}",
            from_email=settings.FROM_EMAIL,
            recipient_list=[request.data["email"]],
            fail_silently=False,
        )
        return Response(status=status.HTTP_202_ACCEPTED)

    elif request.data["username"] and request.data["email"]:
        user = User.objects.create(
            username=request.data["username"], email=request.data["email"]
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="Confirmation Code from Ya.MDB",
            message=f"Confirmation code: {confirmation_code}",
            from_email=settings.FROM_EMAIL,
            recipient_list=[request.data["email"]],
            fail_silently=False,
        )
        return Response(status=status.HTTP_201_CREATED)

    raise serializers.ValidationError(
        "Укажите обязательные поля username и email."
    )


@api_view(["POST"])
def get_token(request) -> Response:
    """Обработчик генерации токена."""

    username = request.data.get("username")
    confirmation_code = request.data.get("confirmation_code")

    if username is None or confirmation_code is None:
        raise serializers.ValidationError(
            "Имя пользователя или код не совпадают либо пусты."
        )

    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

    return Response(status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ModelViewSet):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsUserAdminOrReadOnly,)
    lookup_field = "slug"


class GenreViewSet(ModelViewSet):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsUserAdminOrReadOnly,)
    lookup_field = "slug"


class TitleViewSet(ModelViewSet):
    """Вьюсет для произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("genre__slug", "category__slug", "name", "year")
    permission_classes = (IsUserAdminOrReadOnly,)


class ReviewViewSet(ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsUserAuthenticated, IsUserOwnerOrStaff)

    def get_queryset(self) -> QuerySet:
        """Формирование queryset из отзывов запрашиваемого произведения."""

        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        queryset = Review.objects.filter(title=title)
        return queryset

    def perform_create(self, serializer) -> None:
        """Создание экземпляра отзыва."""

        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        if Review.objects.filter(author=self.request.user, title=title):
            raise serializers.ValidationError(
                "Вы уже оставили отзыв к этому произведению"
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsUserAuthenticated, IsUserOwnerOrStaff)

    def get_queryset(self) -> QuerySet:
        """Формирование queryset из комментариев к определенному отзыву."""
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        queryset = Comment.objects.filter(review=review)
        return queryset

    def perform_create(self, serializer) -> None:
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(ModelViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = (IsUserAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"

    @action(
        methods=("GET", "PATCH"),
        detail=False,
        permission_classes=(IsUserAuthenticated,),
    )
    def me(self, request) -> Response:
        """
        Получение и обновление информации о текущем пользователе.
        """

        if request.method == "PATCH":
            request_data = request.data.copy()
            if request.user.role == 'user':
                request_data['role'] = 'user'
            if request.user.role == 'moderator':
                request_data['role'] = 'moderator'
            serializer = UserSerializer(
                request.user,
                data=request_data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
