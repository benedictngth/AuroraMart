from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal
from django.urls import reverse
from urllib.parse import urlencode
from .models import Product


@require_POST
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
        
    # 4. Unconditional redirect to the constructed URL (either filtered or unfiltered)
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