from django.db import models
from django.contrib.auth.models import User
import uuid

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex'),
    ]

    SUBCATEGORY_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
    ]

    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    image = models.ImageField(upload_to="products/", null=True, blank=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=20, choices=SUBCATEGORY_CHOICES, blank=True, null=True)

    color = models.CharField(max_length=20, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=4.0)

    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_limited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ================= CART =================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ================= WISHLIST =================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ================= ADDRESS =================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.city}"


# ================= ORDER =================
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    order_id = models.CharField(max_length=20, unique=True, blank=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    shipping_address = models.TextField()

    payment_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    return_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = "ORD" + str(uuid.uuid4().hex[:8]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"


# ================= ORDER ITEM =================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ================= REVIEW =================
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    rating = models.IntegerField()
    review = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)


# ================= USER PROFILE =================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username