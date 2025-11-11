from django import forms 
from onlinestore.models import Product, Category, Subcategory, Order
from django.core.exceptions import ValidationError
from django.core import validators
from django.contrib.auth.models import User


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = ['sku_code', 'category', 'subcategory', 'product_name', 'product_description', 'product_rating','unit_price', 'quantity_on_hand', 'reorder_quantity', 'is_active'] 

        
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status']

class StaffProductSortForm(forms.Form):
    SORT_CHOICES = [
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)'),
        
        ('stock_asc', 'Stock (Low to High)'),
        ('stock_desc', 'Stock (High to Low)'),
    ]
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label='Sort by',
    )

class StaffProductFilterForm(forms.Form):
    is_active = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'), 
            ('True', 'Active Only'), 
            ('False', 'Inactive Only')
        ], 
        required=False, 
        label='Status', 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        label='Category',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_stock = forms.IntegerField(
        required=False, 
        label='Min Stock', 
        validators=[validators.MinValueValidator(0, message='Stock cannot be negative.')],
        widget=forms.NumberInput(attrs={'placeholder': 'Min', 'min': '0'})
    )
    max_stock = forms.IntegerField(
        required=False, 
        label='Max Stock', 
        validators=[validators.MinValueValidator(0, message='Stock cannot be negative.')],
        widget=forms.NumberInput(attrs={'placeholder': 'Max', 'min': '0'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        min_stock = cleaned_data.get('min_stock')
        max_stock = cleaned_data.get('max_stock')
        
        if min_stock is not None and max_stock is not None and min_stock > max_stock:
            self.add_error('min_stock', 'Minimum stock cannot be greater than maximum stock.')
            
        return cleaned_data


class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class StaffRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Enter a strong password.")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return password_confirm

class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'subcategory_name']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Smartphones'}),
        }