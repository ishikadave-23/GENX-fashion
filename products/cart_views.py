# cart_views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from .models import Product, Cart, Wishlist

@login_required
@require_POST
def add_to_cart(request):
    """Add product to cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        # Validate product exists
        product = get_object_or_404(Product, id=product_id)
        
        # Check stock availability
        if not product.is_in_stock():
            return JsonResponse({
                'success': False,
                'message': f'Sorry, {product.name} is out of stock!'
            }, status=400)
        
        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Only {product.stock} items available in stock!'
            }, status=400)
        
        # Get or create cart item
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if already exists
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Cannot add {quantity} more items. Only {product.stock - cart_item.quantity} left in stock!'
                }, status=400)
            cart_item.quantity = new_quantity
            cart_item.save()
            message = f'Updated {product.name} quantity in cart!'
        else:
            message = f'{product.name} added to cart!'
        
        # Get updated cart count
        cart_count = Cart.objects.filter(user=request.user).count()
        cart_total = sum(item.total_price() for item in Cart.objects.filter(user=request.user))
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'item_id': cart_item.id,
            'quantity': cart_item.quantity,
            'product_stock_left': product.stock - cart_item.quantity
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def update_cart_quantity(request):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        quantity = int(data.get('quantity'))
        
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        product = cart_item.product
        
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            cart_item.delete()
            message = f'{product.name} removed from cart'
            removed = True
        else:
            # Check stock availability
            if product.stock < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Only {product.stock} items available in stock!'
                }, status=400)
            
            cart_item.quantity = quantity
            cart_item.save()
            message = f'{product.name} quantity updated'
            removed = False
        
        # Get updated cart info
        cart_items = Cart.objects.filter(user=request.user)
        cart_count = cart_items.count()
        cart_total = sum(item.total_price() for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count,
            'cart_total': float(cart_total),
            'removed': removed,
            'item_quantity': cart_item.quantity if not removed else 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def remove_from_cart(request, cart_id):
    """Remove item from cart"""
    try:
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        
        cart_count = Cart.objects.filter(user=request.user).count()
        cart_total = sum(item.total_price() for item in Cart.objects.filter(user=request.user))
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart',
            'cart_count': cart_count,
            'cart_total': float(cart_total)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def add_to_wishlist(request):
    """Add product to wishlist via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check if product already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            message = f'{product.name} added to wishlist!'
            action = 'added'
        else:
            message = f'{product.name} is already in your wishlist'
            action = 'exists'
        
        # Get total wishlist items count
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'wishlist_count': wishlist_count,
            'action': action,
            'item_id': wishlist_item.id,
            'product_name': product.name
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def remove_from_wishlist(request, wishlist_id):
    """Remove item from wishlist"""
    try:
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from wishlist',
            'wishlist_count': wishlist_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def clear_wishlist(request):
    """Clear all wishlist items"""
    try:
        count = Wishlist.objects.filter(user=request.user).count()
        Wishlist.objects.filter(user=request.user).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Cleared {count} item(s) from wishlist',
            'wishlist_count': 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_GET
def get_cart_count(request):
    """Get current cart count"""
    cart_count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})

@login_required
@require_GET
def get_wishlist_count(request):
    """Get current wishlist count"""
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({'wishlist_count': wishlist_count})

@login_required
@require_GET
def get_cart_details(request):
    """Get detailed cart information"""
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    items_data = []
    for item in cart_items:
        items_data.append({
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'total': float(item.total_price()),
            'image_url': item.product.image.url if item.product.image else None,
            'stock': item.product.stock
        })
    
    cart_total = sum(item.total_price() for item in cart_items)
    cart_count = cart_items.count()
    
    return JsonResponse({
        'success': True,
        'items': items_data,
        'total': float(cart_total),
        'count': cart_count
    })

@login_required
@require_GET
def get_wishlist_details(request):
    """Get detailed wishlist information"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    items_data = []
    for item in wishlist_items:
        items_data.append({
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'price': float(item.product.price),
            'image_url': item.product.image.url if item.product.image else None,
            'in_stock': item.product.is_in_stock(),
            'added_at': item.added_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({
        'success': True,
        'items': items_data,
        'count': len(items_data)
    })