from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='admin'):
            return True
        return False


class IsAdminOrServiceEmployeeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name__in=['admin', 'service_employee']):
            return True
        return False
