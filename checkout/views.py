from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages

def checkout(request):
    """ A view to return the checkout page """
    checkout = request.session.get('checkout', {})
    
    if not checkout:
        return redirect('products')
        
    return render(request, 'checkout/checkout.html')

def add_to_checkout(request, item_id):
    """ Add a quantity of the specified product to the checkout """
    quantity = int(request.POST.get('quantity'))
    time_slot = request.POST.get('time_slot')
    booking_date = request.POST.get('booking_date')
    redirect_url = request.POST.get('redirect_url')
    checkout = request.session.get('checkout', {})

    checkout[item_id] = {
        'quantity': quantity,
        'time_slot': time_slot,
        'booking_date': booking_date
    }

    request.session['checkout'] = checkout
    messages.success(request, "Successfully added item to checkout!")
    return redirect(redirect_url)

def remove_from_checkout(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        checkout = request.session.get('checkout', {})
        checkout.pop(item_id)
        request.session['checkout'] = checkout

        if not checkout:
            messages.success(request, "Checkout is now empty")
            return HttpResponse(status=200)
        else:
            messages.success(request, "Item removed from checkout")
            return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)