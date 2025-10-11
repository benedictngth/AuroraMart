from django.urls import path
from . import views

# This list will hold your custom URL patterns for the onlinestore app

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('products/', views.product_list_view, name='product_list'),
]
