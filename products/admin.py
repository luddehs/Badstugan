from django.contrib import admin
from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'description',
        'price',
        'category',
        'location',
        'image',
    )
    ordering = ('name',)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
