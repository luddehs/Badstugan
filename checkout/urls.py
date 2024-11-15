from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('add_to_checkout/<item_id>/', views.add_to_checkout, name='add_to_checkout'),
]
