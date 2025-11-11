from django import forms
from django.contrib.auth.models import User 
from .models import CustomerProfile, Category, Subcategory


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    customer_name = forms.CharField(max_length=100)
    customer_address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile 
        fields = ['age', 'gender', 'employment_status', 'occupation', 'education', 'household_size', 'has_children', 'monthly_income']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
            'occupation': forms.Select(attrs={'class': 'form-control'}),
            'education': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'household_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class ProductSortForm(forms.Form):

    SORT_CHOICES = (
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)'),
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)'),
        ('rating_desc', 'Rating (High to Low)'),
        ('rating_asc', 'Rating (Low to High)'),
    )

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label="Sort By",
    )

    category = forms.IntegerField(required=False)
    subcategory = forms.IntegerField(required=False)

    def clean_sort(self):
        sort_value = self.cleaned_data.get('sort')
        if not sort_value:
            return 'name_asc'
        return sort_value
    
class ProductFilterForm(forms.Form):
    RATING_CHOICES = [
        ('', 'Any Rating'),
        (4, '★★★★ & Up'),
        (3, '★★★ & Up'),
        (2, '★★ & Up'),
        (1, '★ & Up'),
    ]
    
    PRICE_CHOICES = [
        ('', 'Any Price'),
        ('0-25', 'Under $25'),
        ('25-50', '$25 - $50'),
        ('50-100', '$50 - $100'),
        ('100-max', '$100 & Over'),
    ]
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.HiddenInput()
    )

    subcategory = forms.ModelChoiceField(
        queryset=Subcategory.objects.all(),
        required=False,
        empty_label="All Subcategories",
        widget=forms.HiddenInput()
    )

    min_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        label="Minimum Rating",
        widget=forms.Select(attrs={'onchange': 'document.getElementById("filter-form").submit();'})
    )

    price_range = forms.ChoiceField(
        choices=PRICE_CHOICES,
        required=False,
        label="Price Range",
        widget=forms.Select(attrs={'onchange': 'document.getElementById("filter-form").submit();'})
    )