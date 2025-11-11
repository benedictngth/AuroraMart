from django.shortcuts import render, redirect, get_object_or_404
from onlinestore.models import Product, Order, OrderItem, Category
from .forms import ProductForm, StaffLoginForm, StaffRegistrationForm, StaffProductFilterForm, StaffProductSortForm, OrderStatusForm, SubcategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def staff_check(user):
    """Checks if the user is authenticated and a staff member."""
    return user.is_authenticated and user.is_staff

def superuser_check(user):
    """Checks if the user is a superuser."""
    return user.is_superuser

def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('adminpanel:staff_landing')

    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('adminpanel:staff_landing')
            else:
                form.add_error(None, "Invalid credentials or not a staff account.")
    else:
        form = StaffLoginForm()
    return render(request, 'adminpanel/staff_login.html', {'form': form})

def staff_logout_view(request):
    logout(request)
    return redirect('adminpanel:staff_login')

def staff_register_view(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True  # Set the staff flag
            user.save()
            return redirect('adminpanel:staff_landing')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'adminpanel/staff_register.html', {'form': form})

@user_passes_test(staff_check, login_url='/adminpanel/login/')
def staff_landing(request):
    context = {
        'page_title': "Staff Dashboard",
    }
    return render(request, 'adminpanel/staff_landing.html', context)

@user_passes_test(staff_check, login_url='/adminpanel/login/')
def product_list(request):
    filter_form = StaffProductFilterForm(request.GET) 
    sort_form = StaffProductSortForm(request.GET)

    products = Product.objects.all()
    title = "All Products"
    search_query = request.GET.get('q') 

    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) | 
            Q(sku_code__icontains=search_query)
        )
        title = f"Search results for '{search_query}'"

    if filter_form.is_valid():
        cleaned_data = filter_form.cleaned_data
        
        if cleaned_data['category']:
            products = products.filter(category=cleaned_data['category'])
        
        if cleaned_data['is_active'] in ['True', 'False']:
            is_active_bool = (cleaned_data['is_active'] == 'True')
            products = products.filter(is_active=is_active_bool)

        if cleaned_data['min_stock'] is not None:
            products = products.filter(quantity_on_hand__gte=cleaned_data['min_stock'])
        
        if cleaned_data['max_stock'] is not None:
            products = products.filter(quantity_on_hand__lte=cleaned_data['max_stock'])
            
    current_sort = 'name_asc' 
    if sort_form.is_valid():
        current_sort = sort_form.cleaned_data.get('sort', 'name_asc') 
    
    if current_sort == 'stock_asc':
        products = products.order_by('quantity_on_hand')
    elif current_sort == 'stock_desc':
        products = products.order_by('-quantity_on_hand')
    elif current_sort == 'name_desc':
        products = products.order_by('-product_name')
    else: 
        products = products.order_by('product_name')

    context = {
        'products': products,
        'page_title': title,
        'search_query': search_query,
        'filter_form': filter_form,
        'sort_form': sort_form,
    }

    return render(request, "adminpanel/product_list.html", context) 

@user_passes_test(staff_check, login_url='/adminpanel/login/')
def new_product(request):
    if request.method == "POST": 
        form = ProductForm(request.POST)
        if form.is_valid():
            sku_code = form.cleaned_data['sku_code'] 
            category = form.cleaned_data['category']
            subcategory = form.cleaned_data['subcategory']
            product_name = form.cleaned_data['product_name']
            product_description = form.cleaned_data['product_description']
            unit_price = form.cleaned_data['unit_price']
            product_rating = form.cleaned_data['product_rating']
            quantity_on_hand = form.cleaned_data['quantity_on_hand']
            reorder_quantity = form.cleaned_data['reorder_quantity']
            
            product = Product(
                sku_code=sku_code,
                category=category,
                subcategory=subcategory,
                product_name=product_name,
                product_description=product_description,
                unit_price=unit_price,
                product_rating=product_rating,
                quantity_on_hand=quantity_on_hand,
                reorder_quantity=reorder_quantity
            )
            product.save() 
        return redirect("adminpanel:adminpanel_product_list")
        
    else:
        form = ProductForm()
        return render(request, 'adminpanel/create_product.html', {'form': form})

@user_passes_test(staff_check, login_url='/adminpanel/login/')
def modify_product(request, product_pk):
    product = Product.objects.get(pk = product_pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid(): 
            product.sku_code = form.cleaned_data['sku_code']
            product.category = form.cleaned_data['category']
            product.subcategory = form.cleaned_data['subcategory']
            product.product_name = form.cleaned_data['product_name']
            product.product_description = form.cleaned_data['product_description']
            product.unit_price = form.cleaned_data['unit_price']
            product.product_rating = form.cleaned_data['product_rating']
            product.quantity_on_hand = form.cleaned_data['quantity_on_hand']
            product.reorder_quantity = form.cleaned_data['reorder_quantity']
            product.save()
        return redirect("adminpanel:adminpanel_product_list")
    else: 
        
        form = ProductForm(instance=product)
    context = {'form': form, 'product': product, 'page_title': f"Modify {product.product_name}"}
    return render(request, 'adminpanel/modify_product.html', context)

@user_passes_test(staff_check, login_url='adminpanel:staff_login')
def create_subcategory(request):
    if request.method == 'POST':
        form = SubcategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:staff_landing')
    else:
        form = SubcategoryForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Subcategory'
    }
    return render(request, 'adminpanel/create_subcategory.html', context)

@user_passes_test(staff_check, login_url='adminpanel:staff_login')
def order_list(request):
    orders = Order.objects.all().order_by('-order_date_time')
    
    context = {
        'orders': orders,
        'page_title': 'Manage Customer Orders',
    }
    return render(request, "adminpanel/order_list.html", context)


@user_passes_test(staff_check, login_url='/adminpanel/login/')
def order_detail(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    
    order_items = order.orderitem_set.select_related('product')
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('adminpanel:adminpanel_order_detail', order_pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
        
    context = {
        'order': order,
        'order_items': order_items,
        'status_form': form,
        'page_title': f'Order Details: {order.order_number}',
    }
    return render(request, "adminpanel/order_detail.html", context)

@user_passes_test(staff_check, login_url='/adminpanel/login/')
def metrics_dashboard(request):
    """Calculates and displays all 5 dashboard metrics."""

    now = timezone.now()
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(weeks=1)
    last_month = now - timedelta(days=30)
    
    order_metrics = {
        'day': Order.objects.filter(order_date_time__gte=yesterday).count(),
        'week': Order.objects.filter(order_date_time__gte=last_week).count(),
        'month': Order.objects.filter(order_date_time__gte=last_month).count(),
        'all_time': Order.objects.count(),
    }
    
    top_selling_items = OrderItem.objects.filter(
        order__order_date_time__gte=last_month
    ).values('product__product_name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]
    
    low_stock_items = Product.objects.filter(
        quantity_on_hand__lt=10
    ).order_by('quantity_on_hand', 'product_name')
    
    last_month_filter = Q(product__orderitem__order__order_date_time__gte=last_month)

    all_categories_performance = Category.objects.all().annotate(
        total_revenue=Coalesce(
            Sum(
                'product__orderitem__line_subtotal', 
                filter=last_month_filter
            ), 
            Decimal(0)
        )
    ).values('category_name', 'total_revenue')

    best_categories = all_categories_performance.order_by('-total_revenue')[:5]

    worst_categories = all_categories_performance.order_by('total_revenue')[:5]


    context = {
        'page_title': "Sales & Inventory Dashboard",
        'order_metrics': order_metrics,
        'top_selling_items': top_selling_items,
        'low_stock_items': low_stock_items,
        'best_categories': best_categories,
        'worst_categories': worst_categories,
    }

    return render(request, 'adminpanel/metrics_dashboard.html', context)