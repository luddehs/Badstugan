from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments, name='payments'),
    path('payments_success/<order_number>/', views.payments_success, name='payments_success'),
]