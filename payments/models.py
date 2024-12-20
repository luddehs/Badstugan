import uuid
from datetime import timedelta

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField

from products.models import Product


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    original_checkout = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for multiple bookings in the same order.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        self.grand_total = self.order_total
        self.save()

    def is_paid(self):
        return self.status == 'paid'

    def cancel(self):
        """
        Cancel the order and free up associated time slots
        """
        if self.status != 'paid':
            self.status = 'cancelled'
            for item in self.lineitems.all():
                item.release_time_slot()
            self.save()
        else:
            raise ValidationError("Cannot cancel a paid order")

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

    def is_expired(self, expiry_minutes=15):
        """
        Check if pending order is expired (default 15 minutes)
        """
        if self.status == 'pending' and self.created_at:
            expiry_time = self.created_at + timedelta(minutes=expiry_minutes)
            return timezone.now() >= expiry_time
        return False

    def clean(self):
        """
        Additional validation for orders
        """
        if self.created_at and self.is_expired():
            self.status = 'cancelled'
            self.save()
            raise ValidationError("Order has expired")


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    time_slot = models.ForeignKey('products.TimeSlot', null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def clean(self):
        """
        Validate the order line item
        """
        # Check if time slot is in the past
        if self.time_slot.is_past:
            raise ValidationError("Cannot book a time slot in the past")

        # Skip the "already booked" validation for existing line items
        if self._state.adding:
            if self.time_slot.is_booked:
                raise ValidationError("This time slot is already booked")

        # Check if quantity exceeds session limit
        if self.quantity > self.product.session_limit:
            raise ValidationError(
                f"Quantity cannot exceed session limit of {self.product.session_limit}"
            )

        # Check if quantity exceeds remaining capacity
        total_bookings = self.time_slot.bookings.aggregate(
            total=Sum('quantity'))['total'] or 0
        if not self._state.adding:  # Subtract current quantity for existing bookings
            total_bookings -= self.quantity
        remaining_capacity = self.product.capacity - total_bookings
        if self.quantity > remaining_capacity:
            raise ValidationError(
                f"Only {remaining_capacity} spots remaining for this time slot"
            )

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total,
        validate the booking, and handle the time slot booking.
        """
        self.full_clean()  # Run validation
        self.lineitem_total = self.product.price * self.quantity
        
        # Check if this is a new line item
        is_new = self._state.adding
        
        super().save(*args, **kwargs)
        
        if is_new:  # Only mark as booked and create booking for new items
            self.time_slot.is_booked = True
            self.time_slot.save()
            
            from products.models import Booking
            Booking.objects.create(
                time_slot=self.time_slot,
                quantity=self.quantity
            )

    def release_time_slot(self):
        """
        Release the time slot and delete associated booking
        """
        if self.time_slot.is_booked:
            self.time_slot.is_booked = False
            self.time_slot.save()
            
            from products.models import Booking
            Booking.objects.filter(
                time_slot=self.time_slot,
                quantity=self.quantity
            ).delete()

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'