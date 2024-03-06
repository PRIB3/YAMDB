from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserOwnerOrStaff(BasePermission):
    """Проверка доступа для автора или модератора."""

    def has_object_permission(self, request, view, obj) -> bool:
        if (
            request.method in SAFE_METHODS
            or request.user.role == "moderator"
            or request.user.role == "admin"
            or request.user.role == "superuser"
            or request.user.is_superuser
        ):
            return True
        return obj.author == request.user


class IsUserAdminOrReadOnly(BasePermission):
    """Проверка доступа для админа или для чтения."""

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and (
                request.user.role == "admin"
                or request.user.role == "superuser"
                or request.user.is_superuser
            )
        ) or (request.method in SAFE_METHODS)


class IsUserAdmin(BasePermission):
    """Проверка доступа для админа."""

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and (
                request.user.role == "admin"
                or request.user.role == "superuser"
                or request.user.is_superuser
            )
        )


class IsUserAuthenticated(BasePermission):
    """Проверка досутпа для аутентифицированного пользователя."""

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and (
                request.user.role == "user"
                or request.user.role == "moderator"
                or request.user.role == "admin"
                or request.user.role == "superuser"
                or request.user.is_superuser
            )
        ) or (request.method in SAFE_METHODS)
