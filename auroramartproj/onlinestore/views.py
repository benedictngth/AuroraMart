from django.shortcuts import render
from .models import Product

# Create your views here.

def landing_page(request):
    return render(request, 'onlinestore/home.html')

def product_list_view(request):

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