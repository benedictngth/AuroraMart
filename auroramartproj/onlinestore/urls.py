from django.urls import path
from . import views

# This list will hold your custom URL patterns for the onlinestore app

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('products/', views.product_list, name='product_list'), 
    path("product/<str:product_pk>/", views.product_detail, name = "product_detail"), 
    path("login/", views.login_view, name = "login")
]
