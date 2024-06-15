from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from myPurse_v2 import urls as myPurse_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(myPurse_urls))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
