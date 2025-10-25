from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Customer
import random
import string

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer__user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'onlinestore/order_confirmation.html', context)

def generate_order_number():
    # Generates a unique 8-digit number prefixed with 'A'.
    while True:
        digits = ''.join(random.choices(string.digits, k=8))
        order_num = f"A{digits}"
        
        if not Order.objects.filter(order_number=order_num).exists():
            return order_num
        
def order_tracking(request, order_id=None):
    order = None
    order_number_to_track = None
    error_message = None
    order_items = None
    
    if order_id:
        order_number_to_track = order_id
        
    elif request.GET.get('order_number'):
        order_number_to_track = request.GET.get('order_number')
    
    if order_number_to_track:
        try:
            order = Order.objects.get(order_number__iexact=order_number_to_track)
            order_items = OrderItem.objects.filter(order=order)

        except Order.DoesNotExist:
            error_message = f"Order with number '{order_number_to_track}' not found."

    context = {
        'order': order,
        'order_number_input': order_number_to_track if order_number_to_track else '',
        'error_message': error_message,
        'order_items': order_items
    }
    return render(request, 'onlinestore/order_tracking.html', context)

@login_required
def view_all_orders(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return render(request, 'onlinestore/all_orders.html', {'error_message': 'Customer profile not found.'})

    all_orders = Order.objects.filter(customer=customer).order_by('-order_date_time')
    
    context = {
        'all_orders': all_orders
    }
    return render(request, 'onlinestore/all_orders.html', context)