from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ================= HOME =================
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # ================= PRODUCTS =================
    path('products/', views.products, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    # ================= CATEGORIES =================
    path('men/', views.men, name='men'),
    path('women/', views.women, name='women'),

    # ================= CART =================
   path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),

    # ================= WISHLIST =================
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # ================= CHECKOUT =================
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
     path('contact/', views.contact, name='contact'),
    # ================= ORDERS =================
    path("orders/", views.orders, name="orders"),

    # ================= AUTH =================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),  # Add this line
    path('rate-product/<int:id>/', views.rate_product, name='rate_product'),]
    

# MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)