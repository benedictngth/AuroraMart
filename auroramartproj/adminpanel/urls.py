from django.urls import path
from . import views

# This list will hold your custom URL patterns for the adminpanel app
urlpatterns = [
    path('dashboard/', views.staff_landing_page, name='staff_landing'),
    path("order_list/", views.order_list, name="adminpanel_order_list"),
    path("order_detail/<str:order_pk>/", views.order_detail, name="adminpanel_order_detail"),
    
    path("product_list/", views.product_list, name="adminpanel_product_list"),
    path("new_product/", views.new_product, name = "new_product"),
    path("delete_product/<str:product_pk>/", views.delete_product, name = "delete_product"),
    path("modify_product/<str:product_pk>/", views.modify_product, name = "modify_product"),
]