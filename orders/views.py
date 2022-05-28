from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from orders.enums import OrderState
from orders.models import Order, Comment, TimelinePoint
from orders.permissions import IsAdminOrServiceEmployeeUser, \
    IsAllowToSeeOrderComments, IsAdminOrServiceEmployeeOrCustomer, \
    IsAdminOrServiceEmployeeOrSelf, IsAllowToEditOrDeleteComments
from orders.serializers import OrderSerializer, CommentSerializer, UserSerializer, \
    OrderStatusUpdateSerializer, OrderPerformerUpdateSerializer, OrderCreateSerializer, \
    EmployerSerializer, CommentCreationSerializer


class OrderPk(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeOrCustomer]


class Orders(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class UserPk(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeOrSelf]


class UserOrders(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.orders_as_customer


class Employers(generics.ListAPIView):
    queryset = User.objects.filter(groups__name__in=['service_employee']).select_related('profile')
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]


class AvailableEmployers(generics.ListAPIView):
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrServiceEmployeeUser]

    def list(self, request, *args, **kwargs):
        order = Order.objects.get(pk=request.GET['order'])
        queryset = User.objects.select_related('profile').filter(profile__spec_id=order.perf_spec.pk)
        serializer = EmployerSerializer(queryset, many=True)
        return Response(serializer.data)


class StatusChanger(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
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
    serializer_class = CommentCreationSerializer
    permission_classes = [IsAuthenticated, IsAllowToSeeOrderComments]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(order__pk=request.GET['order'], is_active=True)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # TODO можно создать комментарий в закрытой заявке, но нельзя отредактировать его
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)


class CommentsUpdate(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAllowToEditOrDeleteComments]

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.is_active = False
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        request.data['was_edited'] = True
        return super().update(request, *args, **kwargs)


class TimelinePoints(generics.ListAPIView):
    serializer_class = TimelinePoint
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = TimelinePoint.objects.filter(order__pk=request.GET['order'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StatusList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        status_list = [{'status_locale': OrderState.ru(s[0]), 'status': s[0]} for s in OrderState.choices]
        return Response(status_list)
