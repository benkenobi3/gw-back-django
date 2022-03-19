from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.permissions import IsAdminOrServiceEmployeeUser
from orders.serializers import OrderSerializer, OrderStatusUpdateSerializer


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
