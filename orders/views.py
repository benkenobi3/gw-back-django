from django.db import transaction
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from orders.models import Order, Comment
from orders.permissions import IsAdminUser, IsAdminOrServiceEmployeeUser, IsAllowToSeeOrderComments
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
        request.data['customer'] = str(request.user.pk)
        return super().post(request, *args, **kwargs)


class Comments(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAllowToSeeOrderComments]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(order__pk=request.GET['order'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data['user'] = str(request.user.pk)
        return super().create(request, *args, **kwargs)
