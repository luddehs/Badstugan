from django.db import models
from django.utils import timezone

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
