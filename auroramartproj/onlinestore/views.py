from django.shortcuts import render, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required

def landing_page(request):
    return render(request, 'onlinestore/home.html')

@login_required
def product_list(request):

    products = Product.objects.all()
    title = "All Products"
    
    # Check for Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category__id=category_id)
        category_name = products.first().category.category_name if products.exists() else "Category"
        title = f"Products in {category_name}"
        
    # Check for Subcategory filter
    subcategory_id = request.GET.get('subcategory')
    if subcategory_id:
        products = products.filter(subcategory__id=subcategory_id)
        subcategory_name = products.first().subcategory.subcategory_name if products.exists() else "Subcategory"
        title = f"Products in {subcategory_name}"

    context = {
        'products': products,
        'page_title': title
    }
    return render(request, 'onlinestore/product_list.html', context) 

@login_required
def product_detail(request, product_pk):
    product = get_object_or_404(Product, pk = product_pk)
    context = {
        'product': product
    }
    return render(request, "onlinestore/product_detail.html", context) 


