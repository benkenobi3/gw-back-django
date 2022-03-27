from rest_framework import serializers
from rest_framework.serializers import ValidationError

from orders.models import Order, Comment, Image
from orders.enums import OrderState


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'creation_datetime', 'status']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']


class OrderPerformerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'performer']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.status = OrderState.APPOINTED
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'order']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['url']


class OrderCreateSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'title', 'description', 'perf_spec', 'images', 'customer']
        extra_kwargs = {'perf_spec': {'required': True}}

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        if not images_data:
            raise ValidationError({'images': ['This field is required.']})

        order = Order.objects.create(**validated_data)
        for image_data in images_data:
            Image.objects.create(order=order, **image_data)

        return order
