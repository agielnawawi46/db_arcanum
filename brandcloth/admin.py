from django.contrib import admin
from .models import Product, Category, ProductSize, Journal, Cart, CartItem, Order, OrderItem

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductSize)
admin.site.register(Journal)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)