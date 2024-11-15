from django.shortcuts import render
from products.models import Product

# Create your views here.

def checkout(request):
    """ A view to return the checkout page """

    
    return render(request, 'checkout/checkout.html')