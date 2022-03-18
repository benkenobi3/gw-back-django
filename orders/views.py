from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.permissions import IsAdminOrPerformerUser


class Orders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrPerformerUser]


class UserOrders(generics.ListAPIView):
    queryset = Order.objects.filter()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
