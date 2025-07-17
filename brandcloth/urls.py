from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    # ViewSets
    ProductViewSet, CartViewSet, CartItemViewSet, OrderViewSet,
    JournalViewSet, ShippingInfoViewSet, PaymentProofAdminViewSet,AdminProductViewSet
,

    # Function-based views
    register, user_detail, AddToCartView, PaymentProofView, list_payment_proofs,
    verify_payment, input_tracking_number, full_report, order_detail, update_order,

    # Extra API
    CategoryListAPIView
)

# Router untuk ViewSet (otomatis CRUD)
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')  # ✅ JANGAN dobel
router.register('journals', JournalViewSet)
router.register('cartitem', CartItemViewSet, basename='cartitem')
router.register('shipping-info', ShippingInfoViewSet, basename='shipping-info')
router.register('paymentproofs', PaymentProofAdminViewSet, basename='paymentproof-admin')
router.register(r'admin/products', AdminProductViewSet, basename='admin-products')


urlpatterns = [
    # 🔁 Router routes (otomatis dari ViewSet)
    path('', include(router.urls)),

    # 🔐 Auth & User
    path('register/', register, name='register'),
    path('user/', user_detail, name='user-detail'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user/', user_detail),

    # 🛒 Cart
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),

    # 💳 Payment Proof
    path('paymentproof/', list_payment_proofs, name='list-paymentproofs'),
    path('payment/verify/<int:order_id>/', verify_payment, name='verify-payment'),
    path('api/payment-proof/', PaymentProofView.as_view(), name='payment-proof'),
    path('payment-proof/', PaymentProofView.as_view(), name='payment-proof'),
    

    # 📦 Admin: Verifikasi & Tracking
    path('admin/payment-proofs/', list_payment_proofs),
    path('admin/verify-payment/<int:order_id>/', verify_payment),
    path('admin/input-tracking/<int:order_id>/', input_tracking_number),
    path('payment-proof/', PaymentProofView.as_view(), name='payment-proof'),

    # 📊 Laporan
    path('admin/full-report/', full_report),
    path('full-report/', full_report, name='full-report'),

    # 📂 Kategori
    path('categories/', CategoryListAPIView.as_view()),

    # 📦 Detail & Update Order (khusus admin)
    path('api/orders/<int:order_id>/', order_detail, name='order-detail'),
    path('api/orders/<int:order_id>/update/', update_order, name='order-update'),
    
]
