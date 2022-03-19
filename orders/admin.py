from django.contrib import admin
from orders.models import Order, Document, Image, Comment


admin.site.register(Order)
admin.site.register(Document)
admin.site.register(Image)
admin.site.register(Comment)
