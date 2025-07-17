from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *

# ===============================
# ✅ PRODUCT
# ===============================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        return queryset
    
class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

# ✅ CATEGORY
class CategoryListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

# ===============================
# ✅ CART & CHECKOUT
# ===============================

class AdminPaymentProofListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proofs = PaymentProof.objects.select_related('order', 'user')
        serializer = PaymentProofSerializer(proofs, many=True)
        return Response(serializer.data)
    
class CartItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

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

# Tambahan add-to-cart via endpoint alternatif
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

        cart, _ = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(
            cart=cart,
            product_id=product_id,
            quantity=quantity,
            size=size,
            price=price
        )

        return Response({'message': 'Item added to cart'}, status=201)

# ===============================
# ✅ ORDER
# ===============================
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        items_data = request.data.get('items', [])
        if not items_data:
            return Response({'error': 'Order must have at least one item.'}, status=400)

        order = Order.objects.create(
            user=request.user,
            status=request.data.get("status", "pending")
        )

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


# ===============================
# ✅ SHIPPING & PEMBAYARAN
# ===============================
class ShippingInfoViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingInfoSerializer
    queryset = ShippingInfo.objects.all()

    def perform_create(self, serializer):
        order_id = self.request.data.get("order")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        serializer.save(order=order)


class PaymentProofView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentProofSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Bukti pembayaran berhasil diunggah'})
        return Response(serializer.errors, status=400)


    
class PaymentProofAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentProof.objects.all()
    serializer_class = PaymentProofSerializer
    permission_classes = [permissions.IsAdminUser]

# ===============================
# ✅ VERIFIKASI & RESI (ADMIN)
# ===============================
@api_view(['POST'])
@permission_classes([IsAdminUser])
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'payment_done'
    order.save()
    return Response({'message': 'Pembayaran berhasil diverifikasi'})

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

# ✅ ADMIN VIEWSET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_payment_proofs(request):
    if request.user.is_staff:
        proofs = PaymentProof.objects.all()
    else:
        proofs = PaymentProof.objects.filter(user=request.user)
    serializer = PaymentProofSerializer(proofs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request, order_id):
    if not request.user.is_staff:
        return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

    try:
        proof = PaymentProof.objects.get(order__id=order_id)
        proof.verified = True
        proof.save()
        return Response({"detail": "Payment verified successfully"})
    except PaymentProof.DoesNotExist:
        return Response({"detail": "Payment proof not found"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_payment_proofs(request):
    if not request.user.is_staff:
        return Response({"detail": "Unauthorized"}, status=403)

    proofs = PaymentProof.objects.all().order_by('-created_at')
    serializer = PaymentProofSerializer(proofs, many=True)
    return Response(serializer.data)

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

# ===============================
# ✅ JOURNAL
# ===============================
class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]  # Public by default

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        return super().destroy(request, *args, **kwargs)

# ===============================
# ✅ AUTH USER
# ===============================
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
    user.is_active = True
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
            'tracking_number': order.tracking_number,
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
        'is_staff': request.user.is_staff,
        'orders': order_list
    })

# ===============================
# ✅ FULL REPORT ADMIN
# ===============================
@api_view(['GET'])
@permission_classes([IsAdminUser])
def full_report(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()

    orders = Order.objects.filter(status__in=['payment_done', 'shipped'])
    total_orders = orders.count()
    total_revenue = sum(item.price * item.quantity for order in orders for item in order.items.all())

    top_products = OrderItem.objects.values(
        'product__id', 'product__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    return Response({
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'top_products': list(top_products),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    serializer = OrderSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)