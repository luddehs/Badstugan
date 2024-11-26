from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import Product, Category, TimeSlot

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
        'today_date': timezone.now().date(),
    }
    return render(request, 'products/product_detail.html', context)

def get_available_slots(request, product_id):
    """ API view to get available time slots for a specific date """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)

    # Convert string date to datetime
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Get all available slots for the given date
    available_slots = TimeSlot.objects.filter(
        product_id=product_id,
        start_time__date=date,
        is_booked=False,
        start_time__gt=timezone.now()
    ).order_by('start_time')

    slots_data = [{
        'id': slot.id,
        'time': slot.start_time.strftime('%H:%M')
    } for slot in available_slots]

    return JsonResponse({'time_slots': slots_data})
