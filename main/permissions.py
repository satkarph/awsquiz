from rest_framework import permissions


class NormalUserGetOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow GET requests
        if request.method == 'GET' and request.user.is_authenticated:
            return True

        return request.user.is_superuser and request.user.is_authenticated


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser and request.user.is_authenticated