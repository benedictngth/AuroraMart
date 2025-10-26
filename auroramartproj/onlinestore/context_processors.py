from .models import Category, Subcategory, CustomerProfile
from .utils import predict_preferred_category 

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
    recommended_category_name = None

    if request.user.is_authenticated:
        try:
    #age, gender, household_size, has_children, monthly_income_sgd, employment_status, occupation, education
            profile = request.user.customer.customerprofile
            
            customer_data = {
                'age': profile.age,
                'gender': profile.gender,
                'household_size': profile.household_size,
                'has_children': profile.has_children,
                'monthly_income_sgd': profile.monthly_income,
                'employment_status': profile.employment_status,
                'occupation': profile.occupation,
                'education': profile.education
            }
            # Get the first element from the prediction array
            recommended_category_name = predict_preferred_category(customer_data)[0]

        except (CustomerProfile.DoesNotExist, AttributeError):
            # This will catch cases where the user has no customer or profile yet
            pass
    print(recommended_category_name)
    return {
        'recommended_category': recommended_category_name
    }