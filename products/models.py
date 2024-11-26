from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    friendly_name = models.CharField(max_length=254, blank=True, null=True)
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=254, unique=True, default="UNKNOWN_SKU")
    name = models.CharField(max_length=254, default="Unnamed Product")
    description = models.TextField(default="No description available.")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    location = models.CharField(max_length=254, default="Unknown Location")
    capacity = models.PositiveIntegerField(default=1, help_text="Maximum number of guests allowed in total")
    session_limit = models.PositiveIntegerField(
        default=4, 
        help_text="Maximum number of guests allowed per booking session (e.g., 4 for shared saunas)"
    )
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

    def get_first_image(self):
        first_image = self.product_images.first()
        return first_image.image if first_image else self.image

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='product_images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='products/')
    order = models.IntegerField(default=1)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image {self.order} for {self.product.name}"

class TimeSlot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.product.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_past(self):
        if self.start_time is None:
            return False
        return self.start_time < timezone.now()

    def clean(self):
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError('End time must be after start time')

    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta(0)

    def has_conflict(self):
        overlapping = TimeSlot.objects.filter(
            product=self.product,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        return overlapping.exists()

class Booking(models.Model):
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.time_slot} - {self.quantity} guests"