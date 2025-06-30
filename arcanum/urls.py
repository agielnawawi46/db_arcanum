from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('tesadmin/', lambda request: HttpResponse('ADMIN ROUTE TEST OK')),
    path('admin/', admin.site.urls),
    path('api/', include('brandcloth.urls')),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('brandcloth.urls')),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
