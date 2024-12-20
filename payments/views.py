from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product, TimeSlot
from checkout.contexts import checkout_contents

import stripe
import json

@require_POST
def cache_payments_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'checkout': json.dumps(request.session.get('checkout', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def payments(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        checkout = request.session.get('checkout', {})
        
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_checkout = json.dumps(checkout)
            order.save()
            for checkout_item_key, item_data in checkout.items():
                try:
                    product_id = checkout_item_key.split('_')[0]
                    product = Product.objects.get(id=product_id)
                    
                    time_slot_id = item_data.get('time_slot')
                    if not time_slot_id:
                        messages.error(request, "Time slot not found for booking")
                        order.delete()
                        return redirect(reverse('checkout'))
                    
                    time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
                    
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        time_slot=time_slot,
                        quantity=item_data.get('quantity', 1),
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of your bookings wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('checkout'))

                request.session['save_info'] = 'save-info' in request.POST
                return redirect(reverse('payments_success', args=[order.order_number]))
            else:
                messages.error(request, 'There was an error with your form. \
                    Please double check your information.')
    else:
        checkout = request.session.get('checkout', {})
        if not checkout:
            messages.error(request, "There's nothing in your booking at the moment")
            return redirect(reverse('products'))

        current_checkout = checkout_contents(request)
        total = current_checkout['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    template = 'payments/payments.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)

def payments_success(request, order_number):
    """
    Handle successful payments
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Booking successfully processed! \
        Your booking number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'checkout' in request.session:
        del request.session['checkout']

    template = 'payments/payments_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)