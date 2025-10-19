from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Subcategory
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def landing_page(request):
    return render(request, 'onlinestore/home.html')

@login_required
def product_list(request):

    products = Product.objects.all()
    title = "All Products"

    breadcrumb = [{'name': 'All Products', 'url': reverse('product_list')}]
    
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')

    if subcategory_id:
        try:
            subcategory_obj = Subcategory.objects.get(id=subcategory_id)
            products = products.filter(subcategory=subcategory_obj)

            subcategory_name = subcategory_obj.subcategory_name
            title = f"Products in {subcategory_name}"

            parent_category = subcategory_obj.category
            breadcrumb.append({
                'name': parent_category.category_name, 
                'url': f"{reverse('product_list')}?category={parent_category.id}"
            })
            
            breadcrumb.append({
                'name': subcategory_name, 
                'url': f"{reverse('product_list')}?subcategory={subcategory_obj.id}"
            })

        except Subcategory.DoesNotExist:
             # Handle case where subcategory ID is invalid
             title = "Products (Filter Not Found)"

    elif category_id:
        try:
            category_obj = Category.objects.get(id=category_id)
            products = products.filter(category=category_obj)

            category_name = category_obj.category_name
            title = f"Products in {category_name}"

            breadcrumb.append({
                'name': category_name, 
                'url': f"{reverse('product_list')}?category={category_obj.id}"
            })

        except Category.DoesNotExist:
            # Handle case where category ID is invalid
            title = "Products (Filter Not Found)"

    cart = request.session.get('cart', {})
    updated_products = []
    
    for product in products:
        product.cart_quantity = 0 
        product_sku_str = str(product.sku_code)
        
        if product_sku_str in cart:
            product.cart_quantity = cart[product_sku_str]['quantity']
            
        updated_products.append(product)
    
    context = {
        'products': products,
        'page_title': title,
        'breadcrumb': breadcrumb
    }
    return render(request, 'onlinestore/product_list.html', context) 

@login_required
def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk = product_pk)
    cart = request.session.get('cart', {})
    product_sku_str = str(product.sku_code)
    cart_quantity = cart.get(product_sku_str, {}).get('quantity', 0)

    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    redirect_to_cart_flag = request.GET.get('next_page') == 'cart_detail'

    context = {
        'product': product,
        'cart_quantity': cart_quantity,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'redirect_to_cart_flag': redirect_to_cart_flag,
    }
    return render(request, "onlinestore/product_detail.html", context) 


