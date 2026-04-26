from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from .models import Product, Cart, Wishlist, Order, OrderItem, Review
from django.http import HttpResponse
from .models import Order
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import os
from django.conf import settings
from io import BytesIO
from reportlab.platypus import Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


def home(request):
    unisex_products = Product.objects.filter(category='unisex')

    return render(request, 'home.html', {
        'unisex_products': unisex_products
    })

# ================= PRODUCTS =================
def products(request):
    products = Product.objects.all()

    search = request.GET.get("search")
    category = request.GET.get("category")
    color = request.GET.get('color')
    size = request.GET.get('size')

    if search:
        products = products.filter(name__icontains=search)

    if category:
        products = products.filter(category__iexact=category)

    if color:
        products = products.filter(color__iexact=color)

    if size:
        products = products.filter(size__iexact=size)

    context = {
        'products': products
    }
    return render(request, "products/products.html", {"products": products})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'products/product_detail.html', {'product': product})


# ================= CATEGORY =================
def men(request):
    products = Product.objects.filter(category='men')
    return render(request, 'products/men.html', {'products': products})


def women(request):
    products = Product.objects.filter(category='women')
    return render(request, 'products/women.html', {'products': products})

def contact(request):
    return render(request, 'contact.html')


# ================= CART =================
@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # redirect back to same page
    next_url = request.GET.get('next')
    return redirect(next_url if next_url else 'products')

@login_required
def remove_from_cart(request, product_id):
    Cart.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cart')


@login_required


def increase_quantity(request, product_id):
    item = Cart.objects.get(user=request.user, product_id=product_id)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required


def decrease_quantity(request, product_id):
    item = Cart.objects.get(user=request.user, product_id=product_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


# ================= WISHLIST =================
@login_required

def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'items': items})


@login_required

def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    next_url = request.GET.get('next')
    return redirect(next_url if next_url else 'products')


@login_required

def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')


@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Cart.objects.get_or_create(user=request.user, product=product)
    Wishlist.objects.filter(user=request.user, product=product).delete()

    return redirect('cart')


@login_required
def add_to_cart_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({'status': 'success'})


@login_required
def add_to_wishlist_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return JsonResponse({'status': 'success'})


# ================= CHECKOUT =================
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items:
        return redirect("cart")

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        address = request.POST.get("shipping_address")
        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            shipping_address=address,
            status="processing",
            payment_status=True
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        return redirect("order_confirmation", order_id=order.id)

    return render(request, "products/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


# ================= ORDER CONFIRM =================
@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, "products/order_confirmation.html", {
        "order": order,
        "order_items": items
    })


# ================= ORDERS =================
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "products/orders.html", {"orders": orders})


@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    order.status = 'cancelled'
    order.save()
    return redirect('orders')


@login_required

def return_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)

    if request.method == "POST":
        reason = request.POST.get("reason")
        order.status = 'returned'
        order.return_reason = reason
        order.save()

    return redirect('orders')


# ================= INVOICE =================
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # 🌟 CUSTOM STYLES
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=22,
        textColor=colors.black,
        spaceAfter=10
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )

    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT,
        textColor=colors.black
    )

    # 🔥 BRAND HEADER
    elements.append(Paragraph("<b>GENX</b>", title_style))
    elements.append(Paragraph("<font size=10>Premium Fashion Store</font>", styles['Normal']))
    elements.append(Spacer(1, 15))

    # 📄 ORDER INFO BOX
    elements.append(Paragraph(f"<b>Order ID:</b> {order.id}", header_style))
    elements.append(Paragraph(f"<b>Date:</b> {order.created_at.strftime('%d %b %Y, %I:%M %p')}", header_style))
    elements.append(Paragraph(f"<b>Customer:</b> {order.user.username}", header_style))
    elements.append(Spacer(1, 15))

    # 🧾 TABLE HEADER
    data = [["Image", "Product", "Qty", "Price", "Subtotal"]]

    total = 0

    # 🔁 ITEMS
    for item in order.items.all():
        subtotal = item.quantity * item.product.price
        total += subtotal

        # 🖼️ IMAGE FIX
        if item.product.image:
            try:
                img = RLImage(item.product.image.path, width=50, height=50)
            except:
                img = Paragraph("No Image", styles['Normal'])
        else:
            img = Paragraph("No Image", styles['Normal'])

        data.append([
            img,
            Paragraph(f"<b>{item.product.name}</b>", styles['Normal']),
            str(item.quantity),
            f"Rs. {item.product.price}",
            f"Rs. {subtotal}"
        ])

    # 💰 TOTAL ROW
    data.append(["", "", "", "Total", f"Rs. {total}"])

    # 📊 TABLE
    table = Table(data, colWidths=[1.2*inch, 2.5*inch, 0.8*inch, 1.2*inch, 1.2*inch])

    table.setStyle(TableStyle([
        # HEADER
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # BODY
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),

        # ALIGN
        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # PADDING
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),

        # GRID
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),

        # ROW COLORS
        ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),

        # TOTAL ROW
        ("BACKGROUND", (-2, -1), (-1, -1), colors.HexColor("#eeeeee")),
        ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # 💳 PAYMENT INFO
    elements.append(Paragraph(f"<b>Payment Method:</b> {order.payment_method}", styles['Normal']))
    elements.append(Paragraph(f"<b>Status:</b> {order.status}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ❤️ FOOTER
    elements.append(Paragraph(
        "<para align='center'><i>Thank you for shopping with GENX ❤️</i></para>",
        styles['Normal']
    ))

    elements.append(Spacer(1, 5))

    elements.append(Paragraph(
        "<para align='center'><font size=9 color=grey>www.genx.com | support@genx.com</font></para>",
        styles['Normal']
    ))

    doc.build(elements)
    return response

# ================= AUTH =================

@login_required

def rate_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')

        if rating:
            Review.objects.create(
                user=request.user,
                product=product,
                rating=int(rating),
                review=review_text
            )

        return redirect('orders')

    return render(request, 'products/rate_product.html', {'product': product})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # ✅ Redirect based on role
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')   # admin goes to admin panel
            else:
                return redirect('home')      # normal user goes to site

        else:
            messages.error(request, "Invalid username or password ❌")

    return render(request, 'products/login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # ✅ Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        # ✅ Check username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists 😒")
            return redirect("register")

        # ✅ Check email already exists (optional but recommended)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered 📧")
            return redirect("register")

        # ✅ Create user safely
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully 🎉")
        return redirect("login")

    return render(request, "products/register.html")


def logout_view(request):
    logout(request)
    return redirect('home')


# ================= PROFILE =================
@login_required
def profile(request):
    return render(request, 'products/profile.html')


@login_required
def profile_update(request):
    if request.method == "POST":
        request.user.username = request.POST.get('username')
        request.user.save()
        return redirect('profile')

    return render(request, 'products/profile.html')

# ================= STATIC =================
def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

@login_required
def profile(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Update user profile
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        
        # Validate email uniqueness
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('profile')
        
        user.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    return render(request, 'products/profile.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Update user profile
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        
        # Validate email uniqueness
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('profile')
        
        user.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    return redirect('profile')