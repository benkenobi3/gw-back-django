from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from orders.models import Order
from orders.enums import OrderState


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


class IsAllowToSeeOrderComments(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            order_pk = request.GET.get('order', None)
        else:
            order_pk = request.POST.get('order', None)

        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            raise NotFound('Order does not exist')

        if request.user and request.user.groups.filter(name='admin'):
            return True
        elif request.user and request.user.groups.filter(name='service_employee'):
            return order.performer == request.user
        else:
            return order.customer == request.user

    def has_object_permission(self, request, view, obj):
        order = obj

        if request.user and not request.user.groups.filter(name='admin'):
            if order.status in [OrderState.DONE, OrderState.REJECTED]:
                raise PermissionDenied(f'You con not comment {order.status} order')

        return True
