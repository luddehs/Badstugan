from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def all_products(request):
    """ A view to show all products with optional category filtering """
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Get category from URL parameter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__name=category)

    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """ A view to show individual product details """
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
    }
    return render(request, 'products/product_detail.html', context)
