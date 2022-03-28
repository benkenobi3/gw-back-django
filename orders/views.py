from django.db import transaction
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from orders.models import Order, Comment
from orders.permissions import IsAdminUser, IsAdminOrServiceEmployeeUser
from orders.serializers import OrderSerializer, CommentSerializer, \
    OrderStatusUpdateSerializer, OrderPerformerUpdateSerializer, OrderCreateSerializer


class Orders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class UserOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders_as_customer


class StatusChanger(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    # TODO добавить логику с историей изменения статусов
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class PerformerChanger(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderPerformerUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def get_serializer_context(self):
        return {
            'user': self.request.user,
            'order_spec': self.get_object().perf_spec
        }


class CreateOrder(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        request.data['customer'] = str(user.pk)
        return super().post(request, *args, **kwargs)


class Comments(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='admin'):
            return Comment.objects.all()
        if self.request.user.groups.filter(name='service_employee'):
            return Comment.objects.filter(order__in=self.request.user.orders_as_performer)
        return Comment.objects.filter(order__in=self.request.user.orders_as_customer)

    def list(self, request, *args, **kwargs):
        # Comments list of current order
        queryset = self.get_queryset().get(order__pk=kwargs['pk'])
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
