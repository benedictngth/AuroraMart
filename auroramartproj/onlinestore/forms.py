from django import forms
from django.contrib.auth.models import User 
from .models import CustomerProfile

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

        GENDER_CHOICES = [
        ('Male', "Male"),
        ("Female", "Female")
        ]

        widgets = {
            'gender': forms.Select(choices = GENDER_CHOICES)
        }