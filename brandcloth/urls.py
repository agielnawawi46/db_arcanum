from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView 
from .views import AddToCartView

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet, basename='cart')  # ✅ Tambah basename
router.register('orders', OrderViewSet)
router.register('journals', JournalViewSet)
router.register('cartitem', CartItemViewSet, basename='cartitem') 

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register, name='register'),
    path('user/', user_detail, name='user-detail'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]

urlpatterns += [
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),  # ✅ Tambahkan prefix api/
]