from .models import Category, Subcategory

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