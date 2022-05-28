from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from orders.models import Order
from orders.enums import OrderState


class IsAdminOrServiceEmployeeUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name__in=['admin', 'service_employee']):
            return True
        return False


class IsAdminOrServiceEmployeeOrCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and \
                (request.user.groups.filter(name__in=['admin', 'service_employee']) or
                 request.user == obj.customer):
            return True
        return False


class IsAdminOrServiceEmployeeOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and (request.user == obj or request.user.groups.filter(name__in=['admin', 'service_employee'])):
            return True
        return False


class IsAllowToSeeOrderComments(permissions.BasePermission):
    def has_permission(self, request, view):

        order_pk = request.data.get('order', None)
        if not order_pk:
            order_pk = request.query_params.get('order', None)

        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            raise NotFound('Order does not exist')

        if request.user and request.user.groups.filter(name='admin'):
            return True
        else:
            return order.performer == request.user or order.customer == request.user


class IsAllowToEditOrDeleteComments(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        comment = obj

        if request.user and not request.user.groups.filter(name='admin'):
            if comment.order.status in [OrderState.DONE, OrderState.REJECTED]:
                raise PermissionDenied(f'You con not comment {comment.order.status} order')

            if comment.order.customer != request.user or comment.order.performer != request.user:
                raise PermissionDenied(f'You con not change this order')

        return True
