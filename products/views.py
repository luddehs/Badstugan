from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import Product, Category, TimeSlot, Booking
from django.db import models
from .forms import ProductForm

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
    """ API view to get available timeslots for a specific date """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)

    # Convert string date to datetime
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    product = get_object_or_404(Product, id=product_id)
    
    # Get all slots for the given date
    time_slots = TimeSlot.objects.filter(
        product_id=product_id,
        start_time__date=date,
        start_time__gt=timezone.now()
    ).order_by('start_time')

    slots_data = []
    for slot in time_slots:
        # Count total bookings for this slot
        total_bookings = Booking.objects.filter(
            time_slot=slot
        ).aggregate(total_guests=models.Sum('quantity'))['total_guests'] or 0

        # Check if slot has space available
        remaining_capacity = product.capacity - total_bookings
        
        if remaining_capacity > 0 and not slot.is_booked:
            slots_data.append({
                'id': slot.id,
                'time': f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}",
                'duration': f"{slot.duration.total_seconds() / 3600:.1f}",
                'remaining_capacity': remaining_capacity
            })

    return JsonResponse({'time_slots': slots_data})

def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

def edit_product(request, product_id):
    """ Edit a product in the store """
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)

def delete_product(request, product_id):
    """ Delete a product from the store """
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))