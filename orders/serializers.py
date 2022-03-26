from rest_framework import serializers
from orders.models import Order, Comment
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
        model = Comment
        fields = ['id', 'url', 'order']


class CreateOrderSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=True)

    class Meta:
        model = Comment
        fields = ['id', 'title', 'description', 'perf_spec', 'images', 'customer']
        extra_kwargs = {'perf_spec': {'required': True}}
