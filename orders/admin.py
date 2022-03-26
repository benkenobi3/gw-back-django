from django.contrib import admin
from orders.models import Order, Document, Image, Comment, Specialization, Profile


admin.site.register(Order)
admin.site.register(Document)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Specialization)
admin.site.register(Profile)
