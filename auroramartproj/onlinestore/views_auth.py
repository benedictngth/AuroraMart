from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, CustomerProfile
from .forms import RegistrationForm, LoginForm, CustomerProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None: 
                login(request, user)
                return redirect("onlinestore:landing_page") 
            else:
                form.add_error(None, "Invalid username or password")
        return render(request, "onlinestore/login.html", {'form': form})
    else:
        form = LoginForm()
        return render(request, "onlinestore/login.html", {'form': form})

def logout_view(request):
    logout(request)
    return redirect('onlinestore:landing_page')

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create the User object
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Create the related Customer object
            Customer.objects.create(
                user=user,
                customer_name=form.cleaned_data['customer_name'],
                customer_address=form.cleaned_data['customer_address']
            )
            login(request, user)
            return redirect('onlinestore:create_profile') 
    else: 
        form = RegistrationForm() 
        return render(request, "onlinestore/register.html", {'form':form })

@login_required
def create_profile_view(request):
    if request.method == "POST":
        form = CustomerProfileForm(request.POST) 
        if form.is_valid():
            profile = form.save(commit=False) 
            print(request.user)
            profile.customer = request.user.customer
            profile.save()
            return redirect('onlinestore:landing_page')
    else:
        form = CustomerProfileForm()
        return render(request, "onlinestore/create_profile.html", {'form': form})
    
@login_required
def edit_profile_view(request):
    
    try:
        profile = request.user.customer.customerprofile
    except (Customer.DoesNotExist, CustomerProfile.DoesNotExist):
        return redirect('onlinestore:create_profile') 

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('onlinestore:landing_page')
    else:
        form = CustomerProfileForm(instance=profile)

    context = {
        'form': form,
        'is_edit': True 
    }
    return render(request, "onlinestore/edit_profile.html", context)