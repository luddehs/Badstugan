from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, TimeSlot

def checkout_contents(request):
    checkout_items = []
    total = 0
    product_count = 0
    checkout = request.session.get('checkout', {})

    for checkout_item_key, item_data in checkout.items():
        product_id = checkout_item_key.split('_')[0]
        
        if isinstance(item_data, dict):
            product = get_object_or_404(Product, pk=product_id)
            time_slot = get_object_or_404(TimeSlot, pk=item_data['time_slot'])
            total += item_data['quantity'] * product.price
            product_count += item_data['quantity']
            checkout_items.append({
                'item_id': checkout_item_key,
                'quantity': item_data['quantity'],
                'product': product,
                'time_slot': time_slot,
                'booking_date': item_data['booking_date'],
                'subtotal': item_data['quantity'] * product.price
            })

    grand_total = total

    context = {
        'checkout_items': checkout_items,
        'total': total,
        'product_count': product_count,
        'grand_total': grand_total,
    }

    return context