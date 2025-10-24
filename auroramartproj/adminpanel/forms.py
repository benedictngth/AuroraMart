from django import forms 
from onlinestore.models import Product, Category, Subcategory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ['sku_code', 'category', 'subcategory', 'product_name', 'product_description', 'product_rating','unit_price', 'quantity_on_hand', 'reorder_quantity'] 

        
