from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import ShippingInfoViewSet
from .views import PaymentProofView
from .views import list_payment_proofs, verify_payment, input_tracking_number
from .views import PaymentProofAdminViewSet


router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register('journals', JournalViewSet)
router.register('cartitem', CartItemViewSet, basename='cartitem')
router.register(r'shipping-info', ShippingInfoViewSet, basename='shipping-info')
router.register('admin/payment-proofs', PaymentProofAdminViewSet, basename='payment-proof-admin')

urlpatterns = [
    path('', include(router.urls)),

    # Auth
    path('register/', register, name='register'),
    path('user/', user_detail, name='user-detail'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Cart
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),

    # ✅ Shipping Info (Konfirmasi Pembelian)
    path('', include(router.urls)),

    # ✅ Payment Proof (Konfirmasi Pembayaran)
    path('payment-proof/', PaymentProofView.as_view(), name='payment-proof'),

    # ✅ Update status by admin (verifikasi)
    path('api/payment/verify/<int:order_id>/', VerifyPaymentView.as_view(), name='verify-payment'),

    # ✅ Cek status order
    path('api/order/status/<int:order_id>/', OrderStatusView.as_view(), name='order-status'),

    #admin
    path('admin/payment-proofs/', list_payment_proofs),
    path('admin/verify-payment/<int:order_id>/', verify_payment),
    path('admin/input-tracking/<int:order_id>/', input_tracking_number),
]
