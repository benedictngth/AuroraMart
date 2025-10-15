from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product



def add_to_cart(request, product_sku):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))

    product = get_object_or_404(Product, pk = product_sku)

    if product_sku in cart:
        cart[product_sku]['quantity'] += quantity
    else:
        cart[product_sku] = {'quantity': quantity}
     
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def cart_detail(request):

    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0

    for product_sku, item_data in cart.items():
        product = get_object_or_404(Product, pk = product_sku)
        item_subtotal = product.unit_price * item_data["quantity"]
        cart_items.append({
            'product':product,
            'quantity': item_data['quantity'],
            'item_subtotal': item_subtotal
        })
        grand_total += item_subtotal
    
    context = {
        'cart_items': cart_items,
        'grand_total': grand_total
    } 

    return render(request, 'onlinestore/cart_detail.html', context) 

def remove_from_cart(request, product_pk):
    cart = request.session.get('cart', {})

    if product_pk in cart:
        del cart[product_pk]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')