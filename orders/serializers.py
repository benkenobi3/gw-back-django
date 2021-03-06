from datetime import datetime, timedelta

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError

from orders.models import Order, Comment, Image, Specialization, TimelinePoint, Address
from orders.enums import OrderState


class SpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    spec = SpecSerializer(source='profile.spec', read_only=True)
    is_busy = serializers.FloatField(source='profile.is_busy', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'spec', 'is_busy']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'status_locale']
        read_only_fields = ['status_locale']


class OrderPerformerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'performer']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.performer:
            instance.status = OrderState.APPOINTED
        else:
            instance.status = OrderState.CREATED
        instance.save()
        return instance

    def validate_performer(self, value):
        if self.context['user'].groups.filter(name='service_employee'):
            if self.context['order_spec'] == self.context['user'].profile.spec:
                value = self.context['user']
            else:
                raise PermissionDenied('Your spec is different than order perf_spec')
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'order', 'creation_datetime', 'is_active', 'was_edited']
        read_only_fields = ['id', 'user', 'order', 'creation_datetime', 'is_active']


class CommentCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'order']

    @staticmethod
    def validate_text(value):
        if value.replace(' ', '') == '':
            raise ValidationError({'text': ['This field can not be empty.']})
        return value


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['url']


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    performer = UserSerializer()
    perf_spec = SpecSerializer()
    address = AddressSerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'creation_datetime', 'target_datetime', 'address', 'flat_number',
                  'status', 'customer', 'performer', 'images', 'perf_spec', 'status_locale']


class OrderCreateSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'perf_spec', 'images', 'customer', 'address', 'flat_number']
        extra_kwargs = {'perf_spec': {'required': True}}

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        if not images_data:
            raise ValidationError({'images': ['This field is required.']})

        validated_data['target_datetime'] = datetime.now() + timedelta(weeks=2)

        order = Order.objects.create(**validated_data)
        for image_data in images_data:
            Image.objects.create(order=order, **image_data)

        return order


class TimelinePointSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimelinePoint
        fields = '__all__'
        read_only_fields = ['order']
