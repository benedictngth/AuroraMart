from .models import Category, Subcategory, CustomerProfile
from .utils import predict_preferred_category, get_recommended_category 

def nav_bar_data(request):
    categories = Category.objects.all().order_by('category_name')

    menu_data = []
    
    for category in categories:
        menu_item = {
            'category': category,
            'subcategories': Subcategory.objects.filter(category=category).order_by('subcategory_name')
        }
        menu_data.append(menu_item)
    return {'MENU_DATA': menu_data}

def cart_item_count(request):
    cart = request.session.get('cart', {})
    
    total_quantity = sum(item_data.get('quantity', 0) for item_data in cart.values())

    return {
        'cart_total_quantity': total_quantity
    }

def recommended_category_processor(request):
    return {'recommended_category': get_recommended_category(request.user)}