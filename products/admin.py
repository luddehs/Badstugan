from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'price',
        'duration',
        'is_private',
        'requires_membership',
        'image',
    )

    ordering = ('name',)

admin.site.register(Product, ProductAdmin)