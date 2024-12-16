from django.shortcuts import render, redirect
from django.contrib import messages

def checkout(request):
    """ A view to return the checkout page """
    checkout = request.session.get('checkout', {})
    
    if not checkout:
        messages.error(request, "There's nothing in your checkout at the moment")
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
    return redirect(redirect_url)