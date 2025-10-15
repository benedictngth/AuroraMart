from django.urls import path
from . import views
from . import views_cart

# This list will hold your custom URL patterns for the onlinestore app

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('products/', views.product_list, name='product_list'), 
    path("product/<str:product_pk>/", views.product_detail, name = "product_detail"), 
    path("login/", views.login_view, name = "login"),
    
    path("cart/", views_cart.cart_detail, name = "cart_detail"),
    path("cart/add/<str:product_sku>/", views_cart.add_to_cart, name = "add_to_cart"),
    path("cart/remove/<str:product_pk>/", views_cart.remove_from_cart, name="remove_from_cart"),

]
