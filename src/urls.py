from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from orders import urls as api_urls


urlpatterns = [
    re_path('^api/', include(api_urls)),
    re_path('^admin/', admin.site.urls),
    re_path('^auth/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('^auth/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
