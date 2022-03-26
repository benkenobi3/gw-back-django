from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated


from orders.enums import OrderState
from orders.models import Order, Comment
from orders.permissions import IsAdminUser, IsAdminOrServiceEmployeeUser
from orders.serializers import OrderSerializer, CommentSerializer, \
    OrderStatusUpdateSerializer, OrderPerformerUpdateSerializer, CreateOrderSerializer


class Orders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class UserOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders_as_customer


class StatusChanger(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class PerformerChanger(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderPerformerUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def put(self, request, *args, **kwargs):
        if request.user.groups.filter(name='service_employee'):
            request.data['performer'] = request.user.pk
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='service_employee'):
            request.data['performer'] = request.user.pk
        return self.patch(request, *args, **kwargs)


class Comments(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='admin'):
            return Comment.objects.all()
        if self.request.user.groups.filter(name='service_employee'):
            return Comment.objects.filter(order__in=self.request.user.orders_as_performer)

        return Comment.objects.filter(order__in=self.request.user.orders_as_customer)

    @staticmethod
    def _protected(request, *args, **kwargs):

        user = request.user
        order_pk = kwargs['pk']

        request.data._mutable = True
        request.data['user'] = user.pk
        request.data['order'] = order_pk
        request.data._mutable = False

        if user.groups.filter(name='admin'):
            allow = True
        elif user.groups.filter(name='service_employee'):
            allow = user.orders_as_performer.exclude(status__in=[OrderState.DONE, OrderState.REJECTED]) \
                .find(pk=order_pk).count() > 0
        else:
            allow = user.orders_as_customer.exclude(status__in=[OrderState.DONE, OrderState.REJECTED]) \
                .find(pk=order_pk).count() > 0

        if not allow:
            raise ValueError('You con not change this order')

        return request, args, kwargs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().get(pk=kwargs['pk'])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return super().create(self._protected(request, *args, **kwargs))

    def update(self, request, *args, **kwargs):
        return super().update(self._protected(request, *args, **kwargs))

    def destroy(self, request, *args, **kwargs):
        return super().destroy(self._protected(request, *args, **kwargs))


class CreateOrder(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _patch_customer(request, *args, **kwargs):
        user = request.user

        request.data._mutable = True
        request.data['customer'] = user.pk
        request.data._mutable = False

        return request, args, kwargs

    def create(self, request, *args, **kwargs):
        return super().create(self._patch_customer(request, *args, **kwargs))
