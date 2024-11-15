from django.shortcuts import render, redirect


# Create your views here.

def checkout(request):
    """ A view to return the checkout page """

    
    return render(request, 'checkout/checkout.html')

def add_to_checkout(request, item_id):
    """ Add a quantity of the specified product to the checkout """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    checkout = request.session.get('checkout', {})

    if item_id in list(checkout.keys()):
        checkout[item_id] += quantity
    else:
        checkout[item_id] = quantity

    request.session['checkout'] = checkout
    print(request.session['checkout'])
    return redirect(redirect_url)