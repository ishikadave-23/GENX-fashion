from django.contrib import admin
from .models import Product, Cart, Wishlist, Address, Order, OrderItem, UserProfile, Review


# ================= PRODUCT ADMIN =================
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)


# ================= ORDER INLINE =================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ================= ORDER ADMIN =================
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('order_id', 'user__username')
    inlines = [OrderItemInline]


# ================= REVIEW ADMIN =================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username")


# ================= REGISTER MODELS =================
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Address)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(UserProfile)