from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartItemViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'cartitems', CartItemViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
