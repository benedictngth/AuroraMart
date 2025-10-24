from django.urls import path
from . import views

# This list will hold your custom URL patterns for the adminpanel app
urlpatterns = [
    path("product_list/", views.product_list, name="adminpanel_product_list"),
    path("new_product/", views.new_product, name = "new_product"),
    path("delete_product/<str:product_pk>/", views.delete_product, name = "delete_product"),
    path("modify_product/<str:product_pk>/", views.modify_product, name = "modify_product")

]