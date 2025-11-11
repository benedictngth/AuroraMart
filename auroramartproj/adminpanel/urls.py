from django.urls import path
from . import views
app_name = "adminpanel"

# This list will hold your custom URL patterns for the adminpanel app
urlpatterns = [
    path('dashboard/', views.staff_landing, name='staff_landing'),

    path('metrics/', views.metrics_dashboard, name='metrics_dashboard'),
    
    path("order_list/", views.order_list, name="adminpanel_order_list"),
    path("order_detail/<str:order_pk>/", views.order_detail, name="adminpanel_order_detail"),
    
    path("product_list/", views.product_list, name="adminpanel_product_list"),
    path("new_product/", views.new_product, name = "new_product"),
    path("modify_product/<str:product_pk>/", views.modify_product, name = "modify_product"),

    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),
    path('register/', views.staff_register_view, name='staff_register'), 
    path('subcategory/new/', views.create_subcategory, name='adminpanel_create_subcategory'),
]