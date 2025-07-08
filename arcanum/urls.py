from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ Dibutuhkan untuk tesadmin
from brandcloth.views import full_report  # ✅ Dipertahankan untuk jaga-jaga kalau nanti dipakai

urlpatterns = [
    path('tesadmin/', lambda request: HttpResponse('ADMIN ROUTE TEST OK')),  # ✅ Tes endpoint
    path('admin/', admin.site.urls),
    path('api/', include('brandcloth.urls')),  # ✅ Semua endpoint kamu dan timmu ada di sini
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # ✅ JWT login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # ✅ JWT refresh
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
