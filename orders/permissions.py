from rest_framework import permissions


class IsAdminOrPerformerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name__in=['admin', 'performer']):
            return True
        return False
