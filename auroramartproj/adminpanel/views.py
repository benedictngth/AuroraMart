from django.shortcuts import render, redirect, get_object_or_404
from onlinestore.models import Product, Order, OrderItem
from .forms import ProductForm, StaffLoginForm, StaffRegistrationForm, StaffProductFilterForm, StaffProductSortForm, OrderStatusForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q

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
        return render(request, 'adminpanel/modify_product.html', {'form': form})
    
@user_passes_test(staff_check, login_url='/adminpanel/login/')
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