from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить доступ, если пользователь аутентифицирован и является студентом
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Студенты").exists()
        )


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешить доступ, если пользователь аутентифицирован и является преподавателем
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="Преподаватели").exists()
        )

    def has_object_permission(self, request, view, obj):
        # Преподаватели могут управлять любым тестом
        if request.user.groups.filter(name="Преподаватели").exists():
            return True
        # Студенты могут только просматривать тесты
        return obj.owner == request.user
