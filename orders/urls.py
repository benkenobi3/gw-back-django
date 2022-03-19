from django.urls import re_path
from orders.views import Orders, UserOrders, StatusChanger


urlpatterns = [
    re_path('orders/all/', Orders.as_view(), name='orders-list'),
    re_path('orders/my/', UserOrders.as_view(), name='orders-user-list'),
    re_path('orders/status/(?P<pk>.*)', StatusChanger.as_view(), name='orders-status-changer')
]
