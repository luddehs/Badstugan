# products/models.py

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=254, unique=True)
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
