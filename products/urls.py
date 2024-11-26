from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('get-available-slots/<int:product_id>/', views.get_available_slots, name='get_available_slots'),
]
