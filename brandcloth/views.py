from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class CartItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]

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
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

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

        order = Order.objects.create(user=request.user, status='Pending')

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price,
            )

        cart.items.all().delete()

        return Response({'message': 'Checkout berhasil', 'order_id': order.id})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_active = True
    user.save()
    return Response({'message': 'User registered successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
