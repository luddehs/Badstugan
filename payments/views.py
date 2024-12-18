from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def payments(request):
    checkout = request.session.get('checkout', {})
    if not checkout:
        messages.error(request, "There's nothing in your booking at the moment")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'payments/payments.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51PAWkSRpX9AQTc0CK5NATR48Mhb3biWJvZqbBVZLM130nK8HIWQ3ae0xDkBmfinvfTy8KvsgAMzaEYPSzrnZRaqb00wmkhxFsX',
        'client_secret': 'test client secret'
    }

    return render(request, template, context)