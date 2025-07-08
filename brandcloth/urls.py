from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    # ViewSets
    ProductViewSet, CartViewSet, CartItemViewSet, OrderViewSet,
    JournalViewSet, ShippingInfoViewSet, PaymentProofAdminViewSet,

    # Fungsional views
    register, user_detail, AddToCartView, PaymentProofView, list_payment_proofs,
    verify_payment, input_tracking_number, full_report,
    
    # Tambahan tim kamu
    CategoryListAPIView
)

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='orders')
router.register('journals', JournalViewSet)
router.register('cartitem', CartItemViewSet, basename='cartitem')
router.register('shipping-info', ShippingInfoViewSet, basename='shipping-info')
router.register('admin/payment-proofs', PaymentProofAdminViewSet, basename='payment-proof-admin')

urlpatterns = [
    path('', include(router.urls)),

    # 🔐 Auth
    path('register/', register, name='register'),
    path('user/', user_detail, name='user-detail'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 🛒 Cart
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),

    # 💳 Payment Proof
    path('payment-proof/', PaymentProofView.as_view(), name='payment-proof'),

    # 📦 Admin: Verifikasi & Tracking
    # path('api/payment/verify/<int:order_id>/', VerifyPaymentView.as_view(), name='verify-payment'),
    # path('api/order/status/<int:order_id>/', OrderStatusView.as_view(), name='order-status'),
    path('admin/payment-proofs/', list_payment_proofs),
    path('admin/verify-payment/<int:order_id>/', verify_payment),
    path('admin/input-tracking/<int:order_id>/', input_tracking_number),

    # 📊 Laporan
    path('admin/full-report/', full_report),
    path('full-report/', full_report, name='full-report'),

    # 🗂️ Kategori
    path('categories/', CategoryListAPIView.as_view()),
]
