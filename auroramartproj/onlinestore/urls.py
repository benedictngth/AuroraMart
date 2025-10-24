from django.urls import path
from . import views
from . import views_cart
from .import views_auth

# This list will hold your custom URL patterns for the onlinestore app

urlpatterns = [

    #product urls
    path('', views.landing_page, name='landing_page'),
    path('onlinestore/products/', views.product_list, name='product_list'), 
    path("onlinestore/product/<str:product_pk>/", views.product_detail, name = "product_detail"), 
    
    #cart urls
    path("onlinestore/cart/", views_cart.cart_detail, name = "cart_detail"),
    path("onlinestore/cart/add/<str:product_pk>/", views_cart.add_to_cart, name = "add_to_cart"),
    path("onlinestore/cart/remove/<str:product_pk>/", views_cart.remove_from_cart, name="remove_from_cart"), 

    #auth urls
    path("onlinestore/login/", views_auth.login_view, name = "login"),
    path("onlinestore/logout/", views_auth.logout_view, name = "logout"),
    path("onlinestore/register/", views_auth.register_view, name = "register"),
    path("onlinestore/register/create-profile/", views_auth.create_profile_view, name = "create_profile")



]
