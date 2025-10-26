from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal
from django.urls import reverse
from urllib.parse import urlencode
from django.db import transaction
from .models import Product, Order, OrderItem, Customer
from .views_order import generate_order_number

def add_to_cart(request, product_pk):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, pk=str(product_pk)) 

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    
    override_quantity = request.POST.get('update') == 'True'
    product_sku_str = str(product.sku_code) 

    if product_sku_str not in cart:
        cart[product_sku_str] = {
            'quantity': quantity,
            'price': str(product.unit_price) 
        }
    else:
        if override_quantity:
            cart[product_sku_str]['quantity'] = quantity
        else:
            cart[product_sku_str]['quantity'] += quantity
        
        if cart[product_sku_str]['quantity'] < 1:
            del cart[product_sku_str]
     
    request.session['cart'] = cart
    request.session.modified = True

    next_page = request.POST.get('next_page')
    
    if next_page == 'cart_detail':
        return redirect('cart_detail')

    category_id = request.POST.get('category')
    subcategory_id = request.POST.get('subcategory')
    
    query_params = {}
    if category_id:
        query_params['category'] = category_id
    if subcategory_id:
        query_params['subcategory'] = subcategory_id

    url = reverse('product_list')
    if query_params:
        url += '?' + urlencode(query_params)
        
    return redirect(url)

def cart_detail(request):

    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = Decimal(0)

    product_skus = cart.keys()
    products_queryset = Product.objects.filter(sku_code__in=product_skus)
    products_map = {p.sku_code: p for p in products_queryset}
    
    for product_sku, item_data in cart.items():
        product = products_map.get(product_sku)

        if product:
            unit_price = Decimal(item_data.get('price', product.unit_price)) 
            quantity = item_data.get("quantity", 0)

            item_subtotal = unit_price * quantity
        
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

    product = get_object_or_404(Product, pk=str(product_pk)) 
    product_sku_str = str(product.sku_code)
    
    if product_sku_str in cart:
        del cart[product_sku_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')

@require_POST
def checkout(request):
    if not request.user.is_authenticated: #non-logged in customers
        return redirect('login') 
    
    cart = request.session.get('cart', {})
    if not cart: # if empty cart
        return redirect('cart_detail')

    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return redirect('login') 

    grand_total = Decimal(0)
    order_items_data = []
    product_skus = cart.keys()
    products_queryset = Product.objects.filter(sku_code__in=product_skus)
    products_map = {p.sku_code: p for p in products_queryset}

    for product_sku, item_data in cart.items():
        product = products_map.get(product_sku)

        if product and item_data.get('quantity', 0) > 0:
            unit_price = Decimal(item_data.get('price', product.unit_price)) 
            quantity = item_data.get("quantity", 0)

            item_subtotal = unit_price * quantity
            grand_total += item_subtotal

            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'line_subtotal': item_subtotal
            })

    if not order_items_data:
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('cart_detail')
    
    custom_order_number = generate_order_number()
    try:
            new_order = Order.objects.create(
                order_number=custom_order_number,
                customer=customer,
                grand_total=grand_total,
                order_status='Processing'
            )

            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=new_order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    line_subtotal=item_data['line_subtotal']
                )

            del request.session['cart']
            request.session.modified = True
            
    except Exception as e:
        print(f"Error during checkout: {e}")
        return redirect('cart_detail')

    return redirect('order_confirmation', order_id=new_order.pk)