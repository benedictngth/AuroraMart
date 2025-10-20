from django.shortcuts import render, get_object_or_404
import joblib
from .models import Product, Category, Subcategory
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import ProductSortForm, ProductFilterForm

def landing_page(request):
    return render(request, 'onlinestore/home.html')

@login_required
def product_list(request):
    filter_form = ProductFilterForm(request.GET)
    sort_form = ProductSortForm(request.GET)

    products = Product.objects.all()
    title = "All Products"
    current_filter_params = ''
    current_sort = 'name_asc'

    breadcrumb = [{'name': 'All Products', 'url': reverse('product_list')}]
    
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')

    if subcategory_id:
        current_filter_params = f"subcategory={subcategory_id}"
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
             title = "Products (Filter Not Found)"

    elif category_id:
        current_filter_params = f"category={category_id}"
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
            title = "Products (Filter Not Found)"

    if filter_form.is_valid():
        min_rating = filter_form.cleaned_data.get('min_rating')
        if min_rating:
            products = products.filter(product_rating__gte=min_rating)

        price_range = filter_form.cleaned_data.get('price_range')
        if price_range:
            if price_range == '0-25':
                products = products.filter(unit_price__lt=25)
            elif price_range == '25-50':
                products = products.filter(unit_price__gte=25, unit_price__lt=50)
            elif price_range == '50-100':
                products = products.filter(unit_price__gte=50, unit_price__lt=100)
            elif price_range == '100-max':
                products = products.filter(unit_price__gte=100)
                
    if sort_form.is_valid():
        current_sort = sort_form.cleaned_data.get('sort')

    if current_sort == 'price_asc':
        products = products.order_by('unit_price')
    elif current_sort == 'price_desc':
        products = products.order_by('-unit_price')
    elif current_sort == 'rating_asc':
        products = products.order_by('product_rating') 
    elif current_sort == 'rating_desc':
        products = products.order_by('-product_rating') 
    elif current_sort == 'name_desc':
        products = products.order_by('-product_name')
    else:
        products = products.order_by('product_name')
    
    total_count = products.count()

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
        'breadcrumb': breadcrumb,
        'total_count': total_count,
        'current_sort': current_sort, 
        'current_filter_params': current_filter_params, 
        'sort_form': sort_form,
        'filter_form': filter_form,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
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
    recommendations = get_recommendations([product_pk], metric = "lift", top_n = 5) 

    print(recommendations)

    context = {
        'product': product,
        'cart_quantity': cart_quantity,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'redirect_to_cart_flag': redirect_to_cart_flag, 
        'recommendations': recommendations
    }
    return render(request, "onlinestore/product_detail.html", context) 



# use the loaded_rules to extract recommendations
#CleanRide Car Care Shield
def get_recommendations(items, metric='confidence', top_n=3):
    loaded_rules = joblib.load('onlinestore/b2c_products_500_transactions_50k.joblib')
    recommendations = set()
    for item in items:
        # Find rules where the item is in the antecedents
        matched_rules = loaded_rules[loaded_rules['antecedents'].apply(lambda x: item in x)]
        # Sort by the specified metric and get the top N
        top_rules = matched_rules.sort_values(by=metric, ascending=False).head(top_n)
        for _, row in top_rules.iterrows():
            recommendations.update(row['consequents'])
    # Remove items that are already in the input list
    recommendations.difference_update(items)
    product_recs = []
    for rec in list(recommendations)[:top_n]:
        try:
            prod = Product.objects.get(pk=rec)
            product_recs.append(
                {'product_sku': prod.sku_code, 
                 'product_name': prod.product_name,
                 'product_subcategory': prod.subcategory_id})
        except Product.DoesNotExist:
            pass
    return product_recs

