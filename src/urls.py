from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, include
from orders import urls as api_urls


urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path('api/', include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
