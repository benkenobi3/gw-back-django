from django.urls import re_path
from orders.views import Orders, UserOrders, StatusChanger, PerformerChanger, CreateOrder, Comments


urlpatterns = [
    re_path('orders/all', Orders.as_view(), name='orders-list'),
    re_path('orders/list', UserOrders.as_view(), name='orders-user-list'),
    re_path('orders/create', CreateOrder.as_view(), name='orders-create'),
    re_path('orders/(?P<pk>.*)/status', StatusChanger.as_view(), name='orders-status-changer'),
    re_path('orders/(?P<pk>.*)/performer', PerformerChanger.as_view(), name='orders-performer-changer'),
    re_path('orders/(?P<pk>.*)/comments/list', Comments.as_view({'get': 'list'}), name='orders-comments-list'),
    re_path('orders/(?P<pk>.*)/comments/create', Comments.as_view({'post': 'create'}), name='orders-comments-create'),
    re_path('orders/(?P<pk>.*)/comments/update', Comments.as_view({'post': 'update'}), name='orders-comments-update'),
    re_path('orders/(?P<pk>.*)/comments/delete', Comments.as_view({'post': 'destroy'}), name='orders-comments-delete'),
]
