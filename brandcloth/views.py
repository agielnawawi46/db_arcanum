from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PaymentProof, Order
from .serializers import PaymentProofSerializer


from .models import *
from .serializers import *

# ✅ Product
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# ✅ CartItem (read only)
class CartItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

# ✅ Cart
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'add':
            return CartItemWriteSerializer
        return CartSerializer

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        size = request.data.get('size')
        price = request.data.get('price')

        if not all([product_id, size, price]):
            return Response({'error': 'Missing required fields'}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            quantity=quantity,
            size=size,
            price=price
        )

        return Response({'message': 'Item added to cart'})

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Keranjang kosong'}, status=400)

        order = Order.objects.create(user=request.user, status='pending')

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price,
                size=item.size
            )

        cart.items.all().delete()
        return Response({'message': 'Checkout berhasil', 'order_id': order.id})

# ✅ Order
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        items_data = request.data.get('items', [])
        if not items_data:
            return Response({'error': 'Order must have at least one item.'}, status=400)

        order = Order.objects.create(user=request.user, status=request.data.get("status", "pending"))

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
                size=item['size'],
                price=item['price']
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=201)

# ✅ Add to Cart via API
class AddToCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        size = request.data.get('size')
        price = request.data.get('price')

        if not all([product_id, size, price]):
            return Response({'error': 'Missing required fields'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            size=size,
            price=price
        )

        return Response({'message': 'Item added to cart'}, status=201)

# ✅ Shipping Info (konfirmasi pengiriman)
class ShippingInfoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingInfoSerializer
    queryset = ShippingInfo.objects.all()

    def perform_create(self, serializer):
        order_id = self.request.data.get("order")
        if not order_id:
            raise serializers.ValidationError({"order": "Order ID is required."})

        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        serializer.save(order=order)

# ✅ Payment Proof (upload bukti pembayaran)
class PaymentProofView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentProofSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Bukti pembayaran berhasil diunggah'})
        return Response(serializer.errors, status=400)

# ✅ Verifikasi (admin/manual)
class VerifyPaymentView(APIView):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.status = 'payment_done'
        order.save()
        return Response({'message': 'Pembayaran telah diverifikasi'})

# ✅ Cek Status
class OrderStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return Response({'status': order.status})

# ✅ Journal
class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#admin
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_payment_proofs(request):
    proofs = PaymentProof.objects.all().order_by('-created_at')
    data = []
    for proof in proofs:
        data.append({
            'id': proof.id,
            'user': proof.user.username,
            'order_id': proof.order.id,
            'bank': proof.bank,
            'total': proof.total,
            'proof_url': request.build_absolute_uri(proof.proof_image.url),
            'created_at': proof.created_at,
            'status': proof.order.status
        })
    return Response(data)

class PaymentProofAdminViewSet(ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        proofs = PaymentProof.objects.all().order_by('-created_at')
        serializer = PaymentProofSerializer(proofs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)
        order.status = 'payment_done'
        order.save()
        return Response({'message': 'Pembayaran berhasil diverifikasi'})

    @action(detail=True, methods=['post'])
    def set_tracking(self, request, pk=None):
        tracking_number = request.data.get('tracking_number')
        if not tracking_number:
            return Response({'error': 'Tracking number diperlukan'}, status=400)
        order = get_object_or_404(Order, id=pk)
        order.tracking_number = tracking_number
        order.status = 'shipped'
        order.save()
        return Response({'message': 'Nomor resi berhasil disimpan'})
    
# Verifikasi pembayaran & ubah status order
@api_view(['POST'])
@permission_classes([IsAdminUser])
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'payment_done'
    order.save()
    return Response({'message': 'Pembayaran berhasil diverifikasi'})

# Input resi / tracking number
@api_view(['POST'])
@permission_classes([IsAdminUser])
def input_tracking_number(request, order_id):
    tracking_number = request.data.get("tracking_number")
    if not tracking_number:
        return Response({'error': 'Tracking number diperlukan'}, status=400)
    
    order = get_object_or_404(Order, id=order_id)
    order.tracking_number = tracking_number
    order.status = 'shipped'
    order.save()
    return Response({'message': 'Nomor resi berhasil disimpan'})


# ✅ Register & User Detail
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'message': 'User registered successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def user_detail(request):
    orders = Order.objects.filter(user=request.user)
    order_list = []
    for order in orders:
        order_list.append({
            'id': order.id,
            'status': order.status,
            'created_at': order.created_at,
            'items': [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price
                } for item in order.items.all()
            ]
        })
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'orders': order_list
    })
