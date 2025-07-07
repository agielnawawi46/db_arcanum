from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductSize, Journal, Cart, CartItem, Order, OrderItem, PaymentProof 

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductSize)
admin.site.register(Journal)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'bank', 'total', 'created_at', 'preview_image']
    readonly_fields = ['preview_image']

    def preview_image(self, obj):
        if obj.proof_image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.proof_image.url)
        return "(Tidak ada gambar)"

    preview_image.short_description = 'Bukti Pembayaran'