from django.shortcuts import render, redirect
from onlinestore.models import Product, Category, Subcategory
from .forms import ProductForm 
from onlinestore.models import Product
def product_list(request):
    products = Product.objects.all()
    context = {
        'products':products
    }

    return render(request, "adminpanel/product_list.html", context) 

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
        return redirect("adminpanel_product_list")
        
    else:
        form = ProductForm()
        return render(request, "adminpanel/create_product.html", {'form': form})
    

def delete_product(request, product_pk):
    product = Product.objects.get(pk = product_pk)
    product.delete()  
    return redirect("adminpanel_product_list")

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
            #or form.save()
        return redirect("adminpanel_product_list")
    else: 
        
        form = ProductForm(instance=product)
        return render(request, "adminpanel/modify_product.html", {'form':form})





