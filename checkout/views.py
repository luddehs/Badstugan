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

    checkout_item_key = f"{item_id}_{time_slot}"

    if checkout_item_key in checkout:
        messages.error(request, "This timeslot is already in your booking!")
    else:
        checkout[checkout_item_key] = {
            'quantity': quantity,
            'time_slot': time_slot,
            'booking_date': booking_date
        }
        request.session['checkout'] = checkout
        messages.success(request, "Timeslot reserved! Complete your booking to confirm.")

    return redirect(redirect_url)

def remove_from_checkout(request, item_id):
    """Remove the item from the shopping bag"""
    try:
        checkout = request.session.get('checkout', {})
        checkout.pop(item_id)
        request.session['checkout'] = checkout

        if not checkout:
            messages.success(request, "Your booking is now empty. Add a new timeslot to continue.")
            return HttpResponse(status=200)
        else:
            messages.success(request, "Timeslot removed from your booking.")
            return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'An error occurred while removing the timeslot. Please try again. {e}')
        return HttpResponse(status=500)