from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.product.name} - {self.size}"

class Journal(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='journal/')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart - {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    size = models.CharField(max_length=10, default='M')

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.size})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('waiting_verification', 'Waiting Verification'),
        ('payment_done', 'Payment Done'),
        ('shipped', 'Shipped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, default='M')  # ✅ Ditambahkan

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.size})"

class ShippingInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"

class PaymentProof(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    proof_image = models.ImageField(upload_to='payment_proofs/')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Payment for Order #{self.order.id}"